import com.sap.it.api.mapping.*;
import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;
import groovy.xml.*;
import groovy.json.*;
import java.util.regex.*;
import groovy.util.XmlSlurper

import com.sap.it.api.ITApiFactory
import com.sap.it.api.securestore.SecureStoreService
import com.sap.it.api.securestore.UserCredential

import java.io.StringReader
import java.io.StringWriter
import javax.xml.transform.OutputKeys
import javax.xml.transform.Source
import javax.xml.transform.Transformer
import javax.xml.transform.TransformerFactory
import javax.xml.transform.stream.StreamResult
import javax.xml.transform.stream.StreamSource

class InvLogHelper {

	public static final String INV_IDOC_LOG                  = 'CSI Inv Replicate'
	public static final String INV_IDOC_LOG_DEBUG            = 'CSI Inv Replicate - Debug'
	public static final String INV_IDOC_LOG_RESPONSE         = 'CSI Inv Update Response'
	public static final String NOT_SUPPLIED_IN_IDOC          = 'Not supplied in IDOC'
	public static final String NEW_LINE                      = '\n';
	public static final String TAB                           = '\t';

	public static final String FAIL_CREATE_INV               = 'Create Inv Failed'
	public static final String FAIL_JWT_ACCESS               = 'Failure obtaining JWT'
	public static final String FAIL_UPDATE_INV               = 'Update Inv Failed'
	public static final String FAIL_XML_VALIDATION           = 'Validation Errors in IDOC'
	
	// Header variables supplied by IDOC adapter:
	//
	private final String hdr_key_idoc_number           = 'sapidoctransferid'
	private final String hdr_key_idoc_type             = 'sapidoctype'

	Message _message

	def InvLogHelper(Message message) {
		_message = message
	}

	def String getBannerFailCreateInv() {
		return FAIL_CREATE_INV + NEW_LINE + NEW_LINE
	}
	def String getBannerFailJwtAccess() {
		return FAIL_JWT_ACCESS + NEW_LINE + NEW_LINE
	}
	def String getBannerFailUpdateInv() {
		return FAIL_UPDATE_INV + NEW_LINE + NEW_LINE
	}
	def String getBannerFailXmlValidation() {
		return FAIL_XML_VALIDATION + NEW_LINE + NEW_LINE
	}

	def String getIDocNumber() {
		return _message.getHeaders().get(this.hdr_key_idoc_number)
	}
	def String getIDocType() {
		return _message.getHeaders().get(this.hdr_key_idoc_type)
	}
	def String getSenderFromEDI(String xmlStr) {
		def xml = new XmlSlurper().parseText(xmlStr)
		return xml.IDOC.EDI_DC40.SNDPRN.text()
	}
	def String prettyPrintXML(String xmlStr) {
		Source xmlSource = new StreamSource(new StringReader(xmlStr))
		Transformer transformer = TransformerFactory.newInstance().newTransformer()
		transformer.setOutputProperty(OutputKeys.INDENT, 'yes')
		transformer.setOutputProperty("{http://xml.apache.org/xslt}indent-amount", "2")
		StreamResult xmlResult = new StreamResult(new StringWriter())

		transformer.transform(xmlSource,xmlResult)
		return xmlResult.getWriter().toString()
	}
	def String formatHttpResponse(Message message) {
		def response = '' as String
	
		def mHdr = message.getHeaders()
	
		response += 'Request URI (' + mHdr.get('CamelHttpMethod') + ') : ' + mHdr.get('CamelHttpUri') + NEW_LINE
		response += 'Response: [' + mHdr.get('CamelHttpResponseCode').toString()
		response += ', ' + mHdr.get('CamelHttpResponseText').toString() + ']' + NEW_LINE
		response += NEW_LINE + '**********************************' + NEW_LINE
		def responseBody = message.getBody()
		response += (responseBody == null || responseBody.isEmpty() ? 'Empty Response Body' : 'Body: ' + NEW_LINE + responseBody)

		return response
	}
	
}

def Boolean isDebugActive(Message message) {
	def isDebugActive = false

	def logCfgLevel = message.getProperty("SAP_MessageProcessingLogConfiguration") as String
	if (logCfgLevel.contains("logLevel=DEBUG")) {
		isDebugActive = true
	}
	return isDebugActive
}

def Message ScriptLogAfterMapping(Message message) {processData("Script Log After Mapping", "text/xml", message);}
def Message ScriptLogBeforeAuthenticate(Message message) {processData("Script Log Before Authenticate", "text/plain", message);}
def Message ScriptLogAfterAuthenticate(Message message) {processData("Script Log After Authenticate", "text/plain", message);}

def Message processData(String prefix, String dFormat, Message message) {
	def headers = message.getHeaders();
	def body = message.getBody(java.lang.String) as String;
	def messageLog = messageLogFactory.getMessageLog(message);

    if (this.isDebugActive(message)) {

    	for (header in headers) {
    	   messageLog.setStringProperty("header." + header.getKey().toString(), header.getValue().toString())
    	}
    	for (property in properties) {
    	   messageLog.setStringProperty("property." + property.getKey().toString(), property.getValue().toString())
    	}
        if (messageLog != null) {
            
            if (dFormat == "text/json") {
                def json = new JsonSlurper().parseText(body);
                body = "";
               	json.each { 
        			body = body + JsonOutput.prettyPrint(JsonOutput.toJson(it));
               	}
            }
            messageLog.addAttachmentAsString(prefix, body, dFormat);
        }
    }
    return message;
}

def Message LogHttpResponce(Message message) {
                
    // get a map of iflow properties
    def map = message.getProperties();
    def headers = message.getHeaders();

    // get an exception java class instance
    def ex = map.get("CamelExceptionCaught");
    if (ex!=null) {
                    
        // save the http error response as a message attachment 
        def messageLog = messageLogFactory.getMessageLog(message);
        String exBody = '';
        exBody = "*********HTTP Exception Response*********" + InvLogHelper.NEW_LINE;
        exBody += "http.StatusCode:" + ex.getStatusCode() + InvLogHelper.NEW_LINE;
        exBody += "http.StatusText:" + ex.getStatusText() + InvLogHelper.NEW_LINE;
        try {
            exBody += JsonOutput.prettyPrint(ex.getResponseBody());
        } catch (e) {
            exBody += ex.getResponseBody();
        }
        messageLog.addAttachmentAsString("http.ResponseBody", exBody, "text/plain");

        // copy the http error response to an iflow's property
        message.setProperty("http.ResponseBody",ex.getResponseBody());
        // copy the http error response to the message body
        message.setBody(ex.getResponseBody());
        // copy the value of http error code (i.e. 500) to a property
        message.setProperty("http.StatusCode",ex.getStatusCode());
        // copy the value of http error text (i.e. "Internal Server Error") to a property
        message.setProperty("http.StatusText",ex.getStatusText());
        
        headers.put("CamelHttpResponseCode",   500);
        message.setHeader("STATUS_CODE", ex.getStatusCode());
        message.setHeader("STATUS_TEXT", ex.getStatusText());

    } else {
        headers.put("CamelHttpResponseCode", 500);
        message.setHeader("STATUS_CODE", "Unknown");
        message.setHeader("STATUS_TEXT", "Unknown");         
    }
    
    return message;
}

def Message getOAuthCredentials(Message message) {
	def clientCredentials = message.getProperty('oauthCredentialName') as String;
	def secureStoreSvc = ITApiFactory.getService(SecureStoreService.class, null) as SecureStoreService;
	def clientCreds = secureStoreSvc.getUserCredential(clientCredentials) as UserCredential;
	
	message.setProperty('clientId', clientCreds.getUsername());
	message.setProperty('clientSecret', clientCreds.getPassword());
	message.setProperty('accessTokenSvcURL', clientCreds.getCredentialProperties().get('sec:server.url'));

	return message;
}

def Message logSuccessMsg(Message message) {
	def logHelper = new InvLogHelper(message)
	def body = message.getBody(java.lang.String) as String;
	def messageLog = messageLogFactory.getMessageLog(message);

	if (messageLog != null) {
		def successCreate = "IDOC: " + logHelper.getIDocNumber() + " Successfully update product site inventory" + InvLogHelper.NEW_LINE;
	    successCreate += "*******Resonse Body*************" + InvLogHelper.NEW_LINE;
	    successCreate += body;
		messageLog.addAttachmentAsString(InvLogHelper.INV_IDOC_LOG_RESPONSE, successCreate, "text/plain");
	}

	return message;
}
