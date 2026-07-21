// Template: Vitest-flavoured test file.
// Use this only when the project already declares `vitest` in devDependencies.
// File location: <project>/test/<service>.test.js

import { describe, it, beforeEach, expect as vExpect } from 'vitest'
import cds from '@sap/cds'

const { GET, POST, expect, defaults } = cds.test(new URL('..', import.meta.url).pathname)

defaults.path = '<SERVICE_PATH>'

describe('<SERVICE_PATH> (Vitest)', () => {

  beforeEach(async () => {
    // await cds.test.data.reset()
  })

  it('lists <ENTITY>', async () => {
    const { data, status } = await GET `/<ENTITY>?$select=ID`
    expect(status).to.equal(200)
    expect(data.value).to.be.an('array')
  })

  it('rejects an invalid POST', async () => {
    const res = await POST('/<ENTITY>', {}).catch(e => e.response)
    vExpect([400, 422]).toContain(res.status)
  })

})
