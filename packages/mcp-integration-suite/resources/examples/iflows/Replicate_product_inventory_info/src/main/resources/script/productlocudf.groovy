import java.text.SimpleDateFormat;

def String GetUTCTime(String arg1){
	def now = new Date()
	return now.format("yyyy-MM-dd'T'HH:mm:ss'Z'", TimeZone.getTimeZone('UTC'))
	//return now.format("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", TimeZone.getTimeZone('UTC'))
}

def String convertStoreId(String argStoreId){
  if(argStoreId.isNumber()){
      return argStoreId.padLeft(10, '0');
  }
  else{
      return argStoreId;
  }
}