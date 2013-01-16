package cn.jc.spider.util;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.commons.collections.MapUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;

public class HttpTools {

	public static String getContentFromUrlByPost(String url, Map<String, String> paramMap, Map<String, String> headerMap, String encode) {
		long d = System.currentTimeMillis();
		HttpPost httpPost = new HttpPost(url);
		List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(1);
		if (MapUtils.isNotEmpty(paramMap)) {
			for (String key : paramMap.keySet()) {
				nameValuePairs.add(new BasicNameValuePair(key, paramMap.get(key)));
			}
		}
		if (MapUtils.isNotEmpty(headerMap)) {
			for (String key : headerMap.keySet()) {
				httpPost.setHeader(key,headerMap.get(key));
			}
		}
		System.out.println("param:"+nameValuePairs);
		try {
			httpPost.setEntity(new UrlEncodedFormEntity(nameValuePairs));
		} catch (UnsupportedEncodingException e1) {
			e1.printStackTrace();
		}
		DefaultHttpClient httpclient = new DefaultHttpClient();
		HttpResponse response;
		String result = null;
		try {
			response = httpclient.execute(httpPost);
			HttpEntity entity = response.getEntity();
			if (StringUtils.isBlank(encode)) {
				encode = "UTF-8";
			}
			result = EntityUtils.toString(entity, encode);
		} catch (Exception e) {
			e.printStackTrace();
		}
		System.out.println("cost:"+(System.currentTimeMillis() - d));
		return result;
	}
	public static String getContentFromUrlByGet(String url, Map<String, String> paramMap, Map<String, String> headerMap, String encode) {
		long d = System.currentTimeMillis();
		HttpGet httpGet = new HttpGet(url);
		if (MapUtils.isNotEmpty(paramMap)) {
			for (String key : paramMap.keySet()) {
				String prefix = "&";
				if (url.endsWith("&") || url.endsWith("?")){
					prefix = "";
				}
				url += prefix + key + "=" + paramMap.get(key);
			}
		}
		if (MapUtils.isNotEmpty(headerMap)) {
			for (String key : headerMap.keySet()) {
				httpGet.setHeader(key,headerMap.get(key));
			}
		}
		DefaultHttpClient httpclient = new DefaultHttpClient();
		HttpResponse response = null;
		String result = null;
		for (int i = 0;response == null&&i<3;i++) {
			response = dorequest(httpclient,httpGet);
			if (i > 0) {
				System.out.println("链接失败，重试"+i+"次");
			}
		}
		HttpEntity entity = response.getEntity();
		try {
			if (StringUtils.isBlank(encode)) {
				encode = "UTF-8";
			}
			result = EntityUtils.toString(entity, encode);
		} catch (Exception e) {
			System.out.println("出错了，跳过===");
			e.printStackTrace();
		}
		System.out.println("cost:"+(System.currentTimeMillis() - d));
//		System.out.println(result);
//		return null;
		return result;
	}
	private static HttpResponse dorequest(DefaultHttpClient httpclient, HttpGet httpGet) {
		try {
			return httpclient.execute(httpGet);
		} catch (Exception e) {
//			e.printStackTrace();
			return null;
		}
	}
}
