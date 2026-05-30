#!/bin/sh

NACOS_HOST="${NACOS_HOST:-nacos}"
NACOS_PORT="${NACOS_PORT:-8848}"
DATA_ID="${DATA_ID:-TEMPLATE_CONFIG}"
GROUP="${GROUP:-TEMPLATE}"
CONFIG_FILE="${CONFIG_FILE:-/config/template-config.yaml}"

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://$NACOS_HOST:$NACOS_PORT/nacos/v1/cs/configs?dataId=test&group=test" 2>/dev/null)
    if [ "$response" = "200" ] || [ "$response" = "404" ]; then
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "nacos not ready"
    exit 1
fi

existing_config=$(curl -s "http://$NACOS_HOST:$NACOS_PORT/nacos/v1/cs/configs?dataId=$DATA_ID&group=$GROUP" 2>/dev/null)
if [ -n "$existing_config" ] && [ "$existing_config" != "null" ] && [ "$existing_config" != "" ] && [ "$existing_config" != "config data not exist" ]; then
    echo "config exists, skip"
    exit 0
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "config file not found"
    exit 1
fi

CONFIG_CONTENT=$(cat "$CONFIG_FILE")

replace_env_placeholder() {
    key="$1"
    value="$2"
    if [ -n "$value" ]; then
        escaped_value=$(printf '%s' "$value" | sed 's/[\/&]/\\&/g')
        CONFIG_CONTENT=$(printf '%s' "$CONFIG_CONTENT" | sed "s|\${$key}|$escaped_value|g")
    fi
}

replace_env_placeholder "OPENAI_API_KEY" "$OPENAI_API_KEY"
replace_env_placeholder "OPENAI_BASE_URL" "$OPENAI_BASE_URL"
replace_env_placeholder "OPENAI_MODEL" "$OPENAI_MODEL"

response=$(curl -s -X POST "http://$NACOS_HOST:$NACOS_PORT/nacos/v1/cs/configs" \
    -d "dataId=$DATA_ID" \
    -d "group=$GROUP" \
    -d "type=yaml" \
    --data-urlencode "content=$CONFIG_CONTENT" 2>/dev/null)

if [ "$response" != "true" ]; then
    echo "publish failed: $response"
fi

verify_config=$(curl -s "http://$NACOS_HOST:$NACOS_PORT/nacos/v1/cs/configs?dataId=$DATA_ID&group=$GROUP" 2>/dev/null)
if [ -z "$verify_config" ] || [ "$verify_config" = "config data not exist" ]; then
    echo "verify failed"
    exit 1
fi

echo "nacos init complete"
