import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.json.*;
import groovy.xml.*;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

def Message build_response(Message message) {
    

def payload = message.getBody(java.lang.String) as String;

def jsonSlurper = new JsonSlurper();
def parsedPayload = jsonSlurper.parseText(payload);

//By default, Google Ads returns 10000 campaigns per package
//Limit to 1000 for usability/perfprmance reasons
//For more results, the user has to enter more precise filter criteria
JsonBuilder builder = new JsonBuilder();
if ( parsedPayload != null && parsedPayload.results != null ){
    List campaigns = parsedPayload .results.take(1000);
    builder ( results: campaigns.collect{element -> 
                        element 
                     } );
    def results  = JsonOutput.prettyPrint(builder.toString());
    parsedPayload = jsonSlurper.parseText(results);
}

//Build and Compress Response Video Campaigns
def isVideo = parsedPayload.results.collect { it.keySet().contains('video')}[0];
String zipVideoCampaigns;
def jsonBuilderVideo = new groovy.json.JsonBuilder();
if ( isVideo == true ) {
    jsonBuilderVideo {
        rval parsedPayload.results.collect { 
            [ 
                CampaignId: it.campaign.id,
                VideoId: it.video.id,
                //VideoChannelId: it.video.channelId,
                //VideoDuration: it.video.durationMillis,
                //VideoTitle: it.video.title
            ]    
        }
    };
    
    def targetStream = new ByteArrayOutputStream();
    def zipStream = new GZIPOutputStream(targetStream);
    zipStream.write(jsonBuilderVideo.toPrettyString().getBytes('UTF-8'));
    zipStream.close();
    def zippedBytes = targetStream.toByteArray();
    targetStream.close();
    zipVideoCampaigns = zippedBytes.encodeBase64();
}

//Build Response Campaign
def outputBuilder = new StreamingMarkupBuilder();
outputBuilder.encoding = 'UTF-8';
def adWordsResponse = outputBuilder.bind {
        mkp.xmlDeclaration()
        //Declare the namespaces
        namespaces << [ nscm:"https://adwords.google.com/api/adwords/cm/v201506",
                        xsi: 'http://www.w3.org/2001/XMLSchema-instance']  
            nscm.getResponse{
                nscm.rval{
                    parsedPayload.results.each { result ->
                        nscm.entries{
                            nscm.id(result.campaign.id)
                            nscm.name(result.campaign.name)
                            nscm.startDate(result.campaign.startDate.toString().replace("-",""))
                            nscm.endDate(result.campaign.endDate.toString().replace("-",""))
                            nscm.status(result.campaign.status)
                            nscm.advertisingChannelType(result.campaign.advertisingChannelType)
                            nscm.networkSettings{
                                nscm.targetGoogleSearch(result.campaign.networkSettings.targetGoogleSearch)
                                nscm.targetContentNetwork(result.campaign.networkSettings.targetContentNetwork)
                                nscm.targetSearchNetwork(result.campaign.networkSettings.targetSearchNetwork)
                            } 
                        }    
                    }        
                }
                if ( isVideo == true ) {
                    nscm.rvalPayload(zipVideoCampaigns)
                }
            }
};

message.setBody(XmlUtil.serialize(adWordsResponse).toString());

return message;

}