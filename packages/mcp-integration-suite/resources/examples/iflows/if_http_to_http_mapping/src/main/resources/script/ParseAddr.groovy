import com.sap.it.api.mapping.*;

/*Add MappingContext parameter to read or set headers and properties
def String customFunc1(String P1,String P2,MappingContext context) {
         String value1 = context.getHeader(P1);
         String value2 = context.getProperty(P2);
         return value1+value2;
}

Add Output parameter to assign the output value.
def void custFunc2(String[] is,String[] ps, Output output, MappingContext context) {
        String value1 = context.getHeader(is[0]);
        String value2 = context.getProperty(ps[0]);
        output.addValue(value1);
        output.addValue(value2);
}*/

def parseAddress(String address) {
    // Regular expression to match state (2-letter code) and ZIP code (5 or 9 digits) at the end
    def stateZipPattern = ~/([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$/
    def matcher = (address =~ stateZipPattern)
    
    if (matcher.find()) {
        def state = matcher.group(1)
        def zip = matcher.group(2)
        def remaining = address.substring(0, matcher.start()).trim()
        
        // Split remaining part into street and city components
        def cityStreetParts = remaining.split(/, */)
        def city = ""
        def street = ""
        
        if (cityStreetParts.size() == 1) {
            // No commas found - assume entire remaining part is street
            street = remaining
        } else {
            // Last element is city, rest is street
            city = cityStreetParts[-1].trim()
            street = cityStreetParts[0..-2].join(', ').trim()
        }
        
        return [
            street: street,
            city: city,
            state: state,
            zip: zip
        ]
    } else {
        // Return empty map if no match found
        return [:]
    }
}

def String getStreet(String address) { parseAddress(address).street ?: "" }
def String getCity(String address) { parseAddress(address).city ?: "" }
def String getState(String address) { parseAddress(address).state ?: "" }
def String getZip(String address) { parseAddress(address).zip ?: "" }

