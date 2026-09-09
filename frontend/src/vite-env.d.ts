/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ORDER_URL: string
  readonly VITE_AI_URL: string
  readonly VITE_JAEGER_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
