// Template: Mocha-flavoured test file.
// Use this only when the project already declares `mocha` in devDependencies.
// File location: <project>/test/<service>.test.js

const cds = require('@sap/cds')
const { GET, POST, expect, defaults } = cds.test(__dirname + '/..')

defaults.path = '<SERVICE_PATH>'

describe('<SERVICE_PATH> (Mocha)', () => {

  before(async () => {
    // one-time setup
  })

  beforeEach(async () => {
    // await cds.test.data.reset()
  })

  it('lists <ENTITY>', async () => {
    const { data, status } = await GET `/<ENTITY>?$select=ID`
    expect(status).to.equal(200)
    expect(data.value).to.be.an('array')
  })

  it('returns 404 on missing key', async () => {
    const res = await GET('/<ENTITY>(99999999)').catch(e => e.response)
    expect(res.status).to.equal(404)
  })

})
