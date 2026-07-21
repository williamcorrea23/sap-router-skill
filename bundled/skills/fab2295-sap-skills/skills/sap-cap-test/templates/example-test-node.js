// Template: default test file for `cds test` (Node built-in runner).
// Replace <SERVICE_PATH> and <ENTITY> with the target the user gave.
// File location: <project>/test/<service>.test.js

const cds = require('@sap/cds')
const { GET, POST, expect, defaults } = cds.test(__dirname + '/..')

defaults.path = '<SERVICE_PATH>' // e.g. '/odata/v4/catalog'

describe('<SERVICE_PATH>', () => {

  beforeEach(async () => {
    // Reset DB between tests when they mutate data. Comment out if read-only.
    // await cds.test.data.reset()
  })

  it('lists <ENTITY>', async () => {
    const { data, status } = await GET `/<ENTITY>?$select=ID`
    expect(status).to.equal(200)
    expect(data.value).to.be.an('array')
  })

  it('reads a single <ENTITY> by key', async () => {
    const list = await GET `/<ENTITY>?$top=1&$select=ID`
    if (!list.data.value.length) return // skip if empty dataset
    const { ID } = list.data.value[0]
    const { data, status } = await GET(`/<ENTITY>(${ID})`)
    expect(status).to.equal(200)
    expect(data.ID).to.equal(ID)
  })

  it('rejects an invalid POST payload', async () => {
    const { response } = await POST('/<ENTITY>', {}).catch(e => e)
    expect(response.status).to.be.oneOf([400, 422])
  })

})
