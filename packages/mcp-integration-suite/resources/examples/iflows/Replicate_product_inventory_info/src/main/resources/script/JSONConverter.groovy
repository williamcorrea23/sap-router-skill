import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def Message processData(Message message) {
    def body = message.getBody(java.lang.String) as String
    def jsonParser = new JsonSlurper()
    def jsonObject = jsonParser.parseText(body)
    
    //remove root element
    message.setBody(JsonOutput.toJson(jsonObject["element"]))

    return message;
}