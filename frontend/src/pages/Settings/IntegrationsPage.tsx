import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AppLayout } from '../../components/layout/AppLayout'
import { useIntegrations } from '../../hooks/useIntegrations'
import { integrationService } from '../../services/integrationService'

const integrationMeta = {
  gmail: { label: 'Gmail', icon: '📧', desc: 'Sync emails as tasks' },
  slack: { label: 'Slack', icon: '💬', desc: 'Sync Slack messages as tasks' },
  notion: { label: 'Notion', icon: '📝', desc: 'Sync Notion pages as tasks' },
}

export default function IntegrationsPage() {
  const { integrations, isLoading, isSyncing, error, setError, disconnect, syncAll, fetchIntegrations } = useIntegrations()
  const [searchParams, setSearchParams] = useSearchParams()
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [connecting, setConnecting] = useState<string | null>(null)

  useEffect(() => {
    const connected = searchParams.get('connected')
    const err = searchParams.get('error')
    if (connected) {
      setSuccessMsg(`${integrationMeta[connected as keyof typeof integrationMeta]?.label ?? connected} connected successfully!`)
      setSearchParams({}, { replace: true })
      fetchIntegrations()
    } else if (err) {
      setError(`Connection failed: ${err.replace(/_/g, ' ')}`)
      setSearchParams({}, { replace: true })
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const connected = (provider: string) =>
    integrations.find((i) => i.provider === provider && i.is_active)

  const handleConnect = async (provider: string) => {
    setConnecting(provider)
    setError(null)
    try {
      let url = ''
      if (provider === 'gmail') url = await integrationService.getGmailAuthUrl()
      if (provider === 'slack') url = await integrationService.getSlackAuthUrl()
      if (provider === 'notion') url = await integrationService.getNotionAuthUrl()
      if (url) window.location.href = url
    } catch {
      setError(`Failed to start ${provider} connection. Please try again.`)
      setConnecting(null)
    }
  }

  return (
    <AppLayout>
      <div className="flex-1 px-4 py-12 max-w-2xl mx-auto w-full">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-off-white mb-1">Integrations</h1>
              <p className="text-muted-text">Connect your tools to import tasks.</p>
            </div>
            {integrations.length > 0 && (
              <button
                onClick={syncAll}
                disabled={isSyncing}
                className="text-soft-mint text-sm hover:underline disabled:opacity-50"
              >
                {isSyncing ? 'Syncing...' : '↻ Sync All'}
              </button>
            )}
          </div>

          {successMsg && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 px-4 py-3 rounded-xl bg-emerald-900/40 border border-soft-mint/30 text-soft-mint text-sm flex items-center justify-between"
            >
              <span>✓ {successMsg}</span>
              <button onClick={() => setSuccessMsg(null)} className="text-soft-mint/60 hover:text-soft-mint ml-4">✕</button>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 px-4 py-3 rounded-xl bg-amber-900/30 border border-muted-amber/30 text-muted-amber text-sm flex items-center justify-between"
            >
              <span>{error}</span>
              <button onClick={() => setError(null)} className="text-muted-amber/60 hover:text-muted-amber ml-4">✕</button>
            </motion.div>
          )}

          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-slate-900 rounded-2xl h-24 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {Object.entries(integrationMeta).map(([provider, meta]) => {
                const conn = connected(provider)
                const isConnecting = connecting === provider
                return (
                  <motion.div
                    key={provider}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="bg-slate-900 rounded-2xl p-5 border border-slate-800 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <span className="text-3xl">{meta.icon}</span>
                      <div>
                        <p className="text-off-white font-medium">{meta.label}</p>
                        <p className="text-muted-text text-sm">
                          {conn ? (
                            <span className="text-soft-mint">
                              ✓ Connected
                              {conn.last_synced_at && ` · ${new Date(conn.last_synced_at).toLocaleDateString()}`}
                            </span>
                          ) : (
                            meta.desc
                          )}
                        </p>
                      </div>
                    </div>
                    {conn ? (
                      <button
                        onClick={() => disconnect(conn.id)}
                        className="text-muted-text text-sm hover:text-off-white transition-colors"
                      >
                        Disconnect
                      </button>
                    ) : (
                      <button
                        onClick={() => handleConnect(provider)}
                        disabled={isConnecting}
                        className="bg-soft-mint text-deep-slate font-semibold px-4 py-2 rounded-lg text-sm hover:bg-emerald-400 transition-colors disabled:opacity-60"
                      >
                        {isConnecting ? 'Redirecting...' : 'Connect'}
                      </button>
                    )}
                  </motion.div>
                )
              })}
            </div>
          )}
        </motion.div>
      </div>
    </AppLayout>
  )
}
