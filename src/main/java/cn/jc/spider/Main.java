package cn.jc.spider;

import java.util.HashMap;
import java.util.Map;

import cn.jc.spider.util.HttpTools;

public class Main {

	/**
	 * 
	 * 
http://dynamic.12306.cn/TrainQuery/sellTicketStation.jsp

$.post("http://dynamic.12306.cn/TrainQuery/iframeSellTicketStation.jsp", {
city:"北京",
city_new_value:"false",
country:"昌平区",
country_new_value:"false",
province:"北京",
province_new_value:"false"

},
  function(data){
    alert("Data Loaded: " + data);
  });
foreach遍历省
 foreach遍历市
  foreach遍历区
   查询
   获得内容
   可以拼sql写到页面，或者请求远程地址入库

	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		Map<String, String> map = new HashMap<String, String>();
		map.put("city", "%E5%8C%97%E4%BA%AC");
		map.put("city_new_value", "false");
		map.put("country", "%E6%98%8C%E5%B9%B3%E5%8C%BA");
		map.put("country_new_value", "false");
		map.put("province", "%E5%8C%97%E4%BA%AC");
		map.put("province_new_value", "false");
		Map<String, String> header = new HashMap<String, String>();
		header.put("Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
		header.put("Accept-Encoding","gzip, deflate");
		header.put("Accept-Language","zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3");
		header.put("Connection","keep-alive");
		header.put("Cookie","JSESSIONID=0B8309E9748AED093772AFDD67B8DC54; BIGipServerotsweb=2429813002.62495.0000; BIGipServertrainquery=2614690058.64543.0000");
		header.put("Host","dynamic.12306.cn");
		header.put("Referer","http://dynamic.12306.cn/TrainQuery/sellTicketStation.jsp");
		header.put("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/20100101 Firefox/17.0");
		String content = HttpTools.getContentFromUrlByPost("http://dynamic.12306.cn/TrainQuery/iframeSellTicketStation.jsp", map, header, null);
		System.out.println(content);
	}

}
