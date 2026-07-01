import path from "path";
import { projPath } from "../..";

const resourceBasePath = path.resolve(projPath, "./resources/examples/iflows/");


export const availableExamples: {
	[name: string]: { description: string; _path: string };
} = {
	simple_http_srv_to_http: {
		description: `
This Iflow accepts HTTPS requests on <CPI address>/http_endpoint
It uses User Role authentication
Max Body Size is 40MB for a request

It has no mapping functionality and so on

It sends received data to http://targetaddr/dataupload
With a POST request without authentication
        `,
		_path: path.join(resourceBasePath, "if_http_server_to_http_request"),
	},
	replicate_product_inventory_info: {
		description: `
The purpose of this IFLOW is to Replicate Product Inventory Information from SAP to 3rd party
This IFLOW takes an LOISTD from a SAP system as input
It then saves the application ID into the IDOC using a Content Modifier
The IDOC gets converted using a Message Mapping. The source structure is the IDOC
The Target structure is more of a placeholder for the acutal 3rd party system
After the mapping the XML gets converted into JSON using a standard module
Because there is one unneccesary root element left a groovy script removes this with the function processData
Afterwards another groovy script is running which fixes some JSON conversion issues
Then a content modifier wraps the whole message in an array
Before the request to the target system is made, a Request/Reply module is used to collect the response into a log
Then the request gets executed via HTTP using OAUTH2 Authentication and request method PUT
The response is then redirected by the Request/Reply module to a groovy script which logs the HTTP response        
`,
		_path: path.join(resourceBasePath, "Replicate_product_inventory_info"),
	},
	if_simple_http_message_mapping: {
		description: `
Simple Http to HTTP iflow with a message mapping
It also includes XSD types for the mapping
The XSD and mapping represent the conversion between two order formats
`,
		_path: path.join(resourceBasePath, "if_http_to_http_mapping")

	},
	if_google_get_oauth_token: {
		description: `
This iflow is a dependency of if_google_ads_campaigns
It uses credentils to get an OAuth token which is then returned
It uses a ProcessDirect Sender Channel so it can be called from other iflows
		`,
	_path: path.join(resourceBasePath, "if_google_get_oauth_token")
	},
	if_google_ads_campaigns: {
		description: `
Filters and retrieves a list of campaigns from a Google Ads service account
The procedure is as follows:
initial trigger is a SOAP request to /com.sap.hybris.mkt.gaw.campaignServiceRead
First Step is a content modifier which sets some values from the configuration
It then sets central tenant address with groovy script
In addition it also sets API version with a script
It then parses some headers from the request
In the next step it calls a subprocess which I will describe now
It first builds the payload for the request and then gets the oAuth token by a subprocess (see if_google_get_oauth_token)
The last step is to call a processDirect adapter to trigger iflow if_fwd_google_request which sends the request
The request/reply module then returns the response
		`,
		_path: path.join(resourceBasePath, "if_google_ads_campaigns")
	},
	if_fwd_google_request: {
		description: `
This iflow is used via processDirect adapter to execute a HTTP request.
It has a router which checks wheather basic auth or client cert auth should be used
It then gives back the HTTP response via Request/reply module
		`,
		_path: path.join(resourceBasePath, 'if_fwd_google_request')
	}
};