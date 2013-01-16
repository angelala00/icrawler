package cn.jc.spider.demo1;

import java.io.DataOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;

import org.springframework.http.HttpStatus;

import sun.net.www.http.HttpClient;

public class DownLoadFile {

	public String getFileNameByUrl(String url, String contentType){
		url = url.substring(7);
		if (contentType.indexOf("html") != -1) {
			url = url.replaceAll("[\\?/:*|<>\"]", "_") + ".html";
			return url;
		} else {
			return url.replaceAll("[\\?/:*|<>\"]", "_") + "." + contentType.substring(contentType.lastIndexOf("/") + 1);
		}
	}
	private void saveToLocal(byte[] data, String filePath){
		try {
			DataOutputStream out = new DataOutputStream(new FileOutputStream(new File(filePath)));
			for (int i = 0; i < data.length; i++) {
				out.write(data[i]);
			}
			out.flush();
			out.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	public String downloadFile(String url){
		String filePath = null;
//		HttpClient httpClient = new HttpClient();
//		httpClient.getHttpConnectionManager().getParams().setConnectionTimeout(2000);
//		GetMethod getMethod = new GetMethod(url);
//		getMethod.getParams().setParameter(HttpMethodParams.SO_TIMEOUT, 2000);
//		getMethod.getParams().setParameter(HttpMethodParams.RETRY_HANDLER, new DefaultHttpMethodRetryHandler());
//		
//		try {
//			int statusCode = httpClient.executeMethod(getMethod);
//			if (statusCode != HttpStatus.SC_OK) {
//				System.err.println("Method failed:" + getMethod.getStatusLine());
//				filePath = null;
//			}
//			byte[] responseBody = getMethod.getResponseBody();
//			filePath = "D:\\temp\\" + getFileNameByUrl(url, getMethod.getResponseHeader("Content-Type").getValue());
//			saveToLocal(responseBody, filePath);
//		} catch (HttpException e) {
//			e.printStackTrace();
//		} catch (IOException e) {
//			e.printStackTrace();
//		} finally {
//			getMethod.releaseConnection();
//		}
		return filePath;
	}
}
