import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class PostJSONWithHttpURLConnection {
	
	public static void main (String []args) throws IOException{
		//Change the URL with any other publicly accessible POST resource, which accepts JSON request body
		String BASE_URL = "http://localhost:5004/api/grid_data";
        // String BASE_URL = "https://ajna.labin.rf08.srf/ajnaapi/api/grid_data";

		URL url = new URL (BASE_URL);
		
		HttpURLConnection con = (HttpURLConnection)url.openConnection();
		con.setRequestMethod("POST");
		
		con.setRequestProperty("Content-Type", "application/json; utf-8");
		con.setRequestProperty("Accept", "application/json");
		
		con.setDoOutput(true);
		
		//JSON String need to be constructed for the specific resource. 
		//We may construct complex JSON using any third-party JSON libraries such as jackson or org.json
		String jsonInputString = "{\"query\": {\"metadata.carga.conhecimento.conhecimento\": \"151705125927966\" }," +
		"\"projection\": {\"metadata.carga.container.container\": 1, \"_id\": 1}}";
		
		try(OutputStream os = con.getOutputStream()){
			byte[] input = jsonInputString.getBytes("utf-8");
			os.write(input, 0, input.length);			
		}

		int code = con.getResponseCode();
		System.out.println(code);
		
		try(BufferedReader br = new BufferedReader(new InputStreamReader(con.getInputStream(), "utf-8"))){
			StringBuilder response = new StringBuilder();
			String responseLine = null;
			while ((responseLine = br.readLine()) != null) {
				response.append(responseLine.trim());
			}
			System.out.println(response.toString());
		}
	}

}