import { FormEvent, useEffect, useState } from 'react';
import { fetchJson } from './services/api';

type HealthResponse = {
  status: string;
  timestamp: string;
  service: string;
  message: string;
};

type ConfigResponse = {
  nacos_enabled: boolean;
  config_source: string;
  data: {
    database: Record<string, unknown>;
    openai: Record<string, unknown>;
    app: Record<string, unknown>;
  };
};

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [heartbeatMessage, setHeartbeatMessage] = useState('template alive');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setError(null);
    try {
      const [healthData, configData] = await Promise.all([
        fetchJson<HealthResponse>('/health'),
        fetchJson<ConfigResponse>('/api/system/config')
      ]);
      setHealth(healthData);
      setConfig(configData);
      setHeartbeatMessage(String(configData.data.app.heartbeat_message ?? 'template alive'));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'load failed');
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await fetchJson('/api/system/config', {
        method: 'PUT',
        body: JSON.stringify({
          app: {
            heartbeat_message: heartbeatMessage
          }
        })
      });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'save failed');
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-8 px-6 py-10">
        <section className="overflow-hidden rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_left,_rgba(45,212,191,0.25),_transparent_30%),linear-gradient(135deg,_rgba(15,23,42,0.96),_rgba(30,41,59,0.92))] p-8 shadow-2xl shadow-cyan-950/20">
          <div className="max-w-3xl">
            <p className="text-sm uppercase tracking-[0.35em] text-cyan-300">Project Template</p>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight">Tailwind v4 前后端模板</h1>
            <p className="mt-4 text-base leading-7 text-slate-300">
              前端使用 Tailwind CSS v4，后端保留 Nacos 配置读写与基础心跳接口。
            </p>
          </div>
        </section>

        {error ? (
          <section className="rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
            {error}
          </section>
        ) : null}

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
            <h2 className="text-lg font-medium text-white">服务状态</h2>
            <div className="mt-4 space-y-3 text-sm text-slate-300">
              <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
                <span>状态</span>
                <span className="text-emerald-300">{health?.status ?? '-'}</span>
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
                <span>服务</span>
                <span>{health?.service ?? '-'}</span>
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
                <span>心跳消息</span>
                <span>{health?.message ?? '-'}</span>
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
                <span>配置来源</span>
                <span>{config?.config_source ?? '-'}</span>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
            <h2 className="text-lg font-medium text-white">配置演示</h2>
            <form className="mt-4 space-y-4" onSubmit={(event) => void handleSubmit(event)}>
              <label className="block text-sm text-slate-300">
                <span className="mb-2 block">心跳文案</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
                  value={heartbeatMessage}
                  onChange={(event) => setHeartbeatMessage(event.target.value)}
                />
              </label>
              <button
                type="submit"
                disabled={saving}
                className="rounded-full bg-cyan-400 px-5 py-2.5 text-sm font-medium text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {saving ? '保存中...' : '写回配置'}
              </button>
            </form>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
          <h2 className="text-lg font-medium text-white">当前配置快照</h2>
          <pre className="mt-4 overflow-x-auto rounded-2xl bg-black/30 p-4 text-xs leading-6 text-slate-300">
            {JSON.stringify(config?.data ?? {}, null, 2)}
          </pre>
        </section>
      </div>
    </main>
  );
}
