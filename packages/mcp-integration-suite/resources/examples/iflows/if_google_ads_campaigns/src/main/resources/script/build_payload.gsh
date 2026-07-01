import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.xml.XmlUtil;
import groovy.json.*;

def Message processData(Message message) {
	
    def payload = message.getBody(java.lang.String.class)toString();
    def payloadParsed = new XmlSlurper().parseText( payload );
     JsonBuilder builder = new JsonBuilder();
    
    //Predicates
    def videoCampaigns = false;
    def whereClause = "";
    def predicates = "campaign.status != " + "\'" + "REMOVED" + "\'";
    payloadParsed.serviceSelector.predicates.each { p ->
            
            switch ( p.field ) {
                
                case "Name":
                    whereClause = "campaign.name Like " + "\'%" + p.values + "%\'";
                    break;
    
                case  "StartDate":
                    whereClause = "campaign.start_date >= " + "\'" + p.values + "\'";
                    break;
                
                case "EndDate":
                    whereClause = "campaign.end_date >= " + "\'" + p.va + ls + "\'";
                    break;
                    
                case "Status":
                    whereClause = "campaign.status = " + "\'" + p.values + "\'";
                    break;
                    
                case "AdvertisingChannelType":
                    whereClause = "campaign.advertising_channel_type = " + "\'" + p.values + "\'";
                    if ( p.values == "VIDEO" ) {
                        videoCampaigns = true;
                    }

                    break;
                
                case "TargetGoogleSearch":
                    whereClause = "campaign.network_settings.target_google_search = " + p.values;
                    break;
            
                case "TargetContentNetwork":
                    whereClause = "campaign.network_settings.target_content_network = " + p.values;  
                    break;
            }
            
            if ( whereClause?.trim() ) {
                predicates = predicates + " and " + whereClause;
            }
        }
    
    
    //Select fields
    def requestedFields = "campaign.id, campaign.name, campaign.status,campaign.advertising_channel_type," +
                         "campaign.start_date,campaign.end_date,campaign.network_settings.target_google_search," +
                         "campaign.network_settings.target_content_network";   
   
    //Buid API request Body
   def query_str = "";
   if ( videoCampaigns == true ) {
       requestedFields =  requestedFields + ",video.id"; //",video.channel_id,video.id,video.title,video.duration_millis"
       query_str = "SELECT " +   requestedFields + 
                    " FROM video" +
                    " WHERE " + predicates +
                    " ORDER BY campaign.id";
   } else {
    query_str = "SELECT " +   requestedFields + 
                    " FROM campaign" +
                    " WHERE " + predicates;
   }
   
   
    builder { query         query_str };
    
    def getCampaignsRequest = JsonOutput.prettyPrint(builder.toString());
    message.setBody(getCampaignsRequest);
    
  
	return message;
}