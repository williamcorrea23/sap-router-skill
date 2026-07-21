// Template: testing a bound or unbound action.
// Replace <SERVICE_PATH>, <ENTITY>, <ACTION>, and the payload.
// File location: <project>/test/<service>-action.test.js

const cds = require('@sap/cds')
const { POST, expect, defaults } = cds.test(__dirname + '/..')

defaults.path = '<SERVICE_PATH>'

describe('<SERVICE_PATH> action <ACTION>', () => {

  it('invokes <ACTION> on the service successfully', async () => {
    const { data, status } = await POST('/<ACTION>', {
      // example payload — adjust to the action's signature
      // book: 201, quantity: 5
    })
    expect(status).to.equal(200)
    expect(data).to.exist
  })

  it('returns a structured error when called with an invalid payload', async () => {
    const res = await POST('/<ACTION>', { /* bad payload */ }).catch(e => e.response)
    expect(res.status).to.be.oneOf([400, 422])
    expect(res.data).to.containSubset({ error: {} })
  })

  // Bound action on a specific entity instance:
  it('invokes bound action <ACTION> on <ENTITY>(ID)', async () => {
    // const { data, status } = await POST('/<ENTITY>(<ID>)/<ACTION>', { /* payload */ })
    // expect(status).to.equal(200)
  })

})
