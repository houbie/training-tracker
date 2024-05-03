import { Configuration, DefaultApi } from './generated'

const cfg = new Configuration({
  basePath: process.env.REACT_APP_API_URL,
})

export const api = new DefaultApi(cfg)
