import java.util.HashMap;
import com.sap.gateway.ip.core.customdev.util.Message;
import com.fasterxml.jackson.core.JsonGenerationException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

class jsonEKPOSfix {
    
    public String logical_system = "";
    
    def String fixJSON(String element) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode rootNode = mapper.readTree(element);

        return rootNode.toString();
    }

    def String fixJSONLogicalSystem(String element) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode rootNode = mapper.readTree(element);
        
        if (rootNode.isArray()) {
            for (JsonNode jsonNode : rootNode) {
                
                if (jsonNode.get("logicalSystem") == null) {
                    jsonNode.put("logicalSystem", logical_system);
                } else {
                    // this one should only occur once at the start
                    logical_system = jsonNode.get("logicalSystem").asText();
                }
            }
        }
        return rootNode.toString();
    }
}
    

def Message processData(Message message) {
    
    def ekposJsonConv = new jsonEKPOSfix()

    def messageLog = messageLogFactory.getMessageLog(message);
	def bodyString = message.getBody(java.lang.String) as String;
	def jsonString = ekposJsonConv.fixJSON(bodyString);
	def jsonStringFixed = ekposJsonConv.fixJSONLogicalSystem(jsonString);
	message.setBody(jsonStringFixed);
	
	message.setHeader("X-User-ID", "12");
    message.setHeader("X-Tenant-ID", "0");
    message.setHeader("X-Tenant-Detail", false);
    message.setHeader("Content-Type", "application/json");


    return message;
}