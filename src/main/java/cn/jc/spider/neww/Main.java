package cn.jc.spider.neww;

import org.apache.torque.linkage.SpiderJcMapInit;

public class Main {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		
		SpiderJcMapInit.init_my();
		
		//启动一个爬虫子线程，
		//Crawler
		Runnable target = new Crawler();
		Thread t = new Thread(target);
		t.start();
		//定时(或者通知)检测一个爬虫子线程能否完成任务
		//如果能,则继续,
		//如果不能,估算大致需要多少个进程,估算系统资源,判断是开多少个线程,
		//如果还不够用,考虑是否多台计算机配合工作,检测可用分布式资源,预算分配等
		//继续等待检测系统健康状态
		//此为守护线程
		
		
	}

}
