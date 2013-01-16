package cn.jc.spider.demo1;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class FindData {

	private String url;
	private String website;
	public FindData() {
		super();
	}

	public FindData(String website,String url) throws IOException {
		super();
		this.url = url;
		this.website = website;
		loadContent(url);
	}

	public Map<String, String> findObject(Map<String, Map<String, String>> map) {
		Map<String, String> map1 = new HashMap<String, String>();
		for (String attributeName : map.keySet()) {
			System.out.println(this.url + "::" + map.get(attributeName).get("reg"));
			map1.put(attributeName, findAttribute(map.get(attributeName).get("reg"), Integer.parseInt(map.get(attributeName).get("index"))));
		}
		map1.put("appurl", url);
		map1.put("website", website);
		return map1;
	}

	private void loadContent(String url) throws IOException {
		URL urll = new URL(url);
		Reader reader = new InputStreamReader(new BufferedInputStream(
				urll.openStream()));
		int c;
		StringBuilder sb = new StringBuilder();
		while ((c = reader.read()) != -1) {
			sb.append((char) c);
		}
		this.content = sb.toString();
	}

	/**
	 * 根据一个正则表达式，拿出来想要找的内容
	 * 
	 * @param name
	 * @param reg
	 * @return
	 */
	private String findAttribute(String reg, int groupIndex) {
		String result = null;
		Pattern p = Pattern.compile(reg);
		Matcher m = p.matcher(content);
//		Pattern.compile(reg).matcher(content).find();
		int i = 0;
		while (m.find()) {//这种方式是不是对的，一直还没理解透API
			if (groupIndex > m.groupCount()) {
				System.out.println("警告：正则的捕获组个数没弄明白？");
				continue;
			}
			result = m.group(groupIndex);
			i++;
		}
		if (i > 1) {
			System.out.println("警告：有多个匹配结果");
		}
		// boolean b = m.matches();
		// System.out.println(b);
		return result;
	}

	// adccccadcccccadccad
	//<img class=\"img265_s\" src=\"http://imga.mumayi.com/android/img_mumayi/9/91988/96ea1dddd6985cc01e9c9591097e0d1d.jpg\" title=\"小鸡跑跑\" alt=\"小鸡跑跑\"  /></a><h2 class=\"infosoft\">软件简介</h2>			\r\n				<p>一款简单的考验玩家反应能力的游戏，让小鸡在不受到任何的伤害情况下吃到越多星星越厉害！</p>					<em class=\"titl\">软件大小：</em> \r\n					<em class=\"titr\">0.32 MB</em><h1 class=\"text1\" id=\"titleInner\">小鸡跑跑 V1.0</h1>
	private String content = "";// android;salfdkjas;lfkjsa;lfkjsadf;iuweroiksafjlisuadflksnfksafKJ>JKL>DSFJL<aksfl;jsafkhref='/android/sheyingtuxiang'>摄影图像</a>|<a
																					// href='/android/anquanshadu'>安全杀毒</a>|<a
																					// href='/android/xinwenzixun'>新闻资讯</a>|<a

	public static void main(String args[]) throws IOException {
		FindData fd = new FindData();
		fd.loadContent("http://www.mumayi.com/android-38442.html");
//		fd.content = "aacdef\r\ngg"; 
		
		String sss = fd.findAttribute("软件简介</h2>\\s{0,10}<p>((.|\\s){0,800})</p>\\s{0,10}<div id=\"headshowlogo\">", 1);
		System.out.println(sss);
//		FindData fd = new FindData();
//		System.out.println(fd.findAttribute("titleInner\">(.*)<", 1));
//		System.out.println(fd.findAttribute("<em class=\"titl\">软件大小：</em>(\\s*)<em class=\"titr\">(.*)</em>", 2));
//		System.out.println(fd.findAttribute("<h2 class=\"infosoft\">软件简介</h2>(\\s*)<p>(.*)</p>", 2));
//		System.out.println(fd.findAttribute("<img class=\"img265_(s|h)\" src=\"(.*)\" title=\"(.*)\" alt=\"(.*)\"  />", 2));

		//
		// String reg="^(?!.*(不合谐)).*$";//用到了前瞻
		// System.out.println("不管信不信,反正现在很不合谐".matches(reg));//false不通过
		// System.out.println("不管信不信,反正现在非常合谐".matches(reg));//true通过
		// System.out.println("不合谐在某国是普遍存在的".matches(reg));//false不通过
	}
}
