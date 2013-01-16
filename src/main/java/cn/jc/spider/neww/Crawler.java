package cn.jc.spider.neww;

import java.util.List;
import java.util.Map;

import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.collections.MapUtils;
import org.apache.torque.TorqueException;
import org.apache.torque.util.BasePeer;
import org.apache.torque.util.Criteria;

import cn.jc.spider.po.Task;
import cn.jc.spider.po.Unvisitedurl;
import cn.jc.spider.po.UnvisitedurlPeer;
import cn.jc.spider.util.HttpTools;
import cn.jc.spider.util.ParserTools;

public class Crawler implements Runnable {

	@Override
	public void run() {
		long sleeptime = 14000;
		for(;;){
			int timetime = 2;
			//从队列里拿出任务开始执行
			Task task = TaskQueue.getTask(timetime);//第一个队列，可用于扩展多线程，多进程，多机器执行
			//检测队列,(如果任务很多,通知守护线程(其它子线程),然后继续执行后面任务)
			//如果没有任务,等待若干秒后再次检查,(通知守护线程(其它子线程))
			if (task == null){
				System.out.println("没有任务需要执行 等待");
				sleeptime = 14000;
			} else {
				System.out.println("开始执行任务 task:"+task);
				//检查URLqueue_target，拿出URL
				//这里要不要多线程，（分布式？轮换IP代理？如果要求爬虫速度的时候，可考虑改成多线程或者分布式的（子线程控制权限当前线程，或者再加一个线程？），）
				Unvisitedurl url = null;
				for(;;){
					try {
						Thread.sleep(1000);
					} catch (InterruptedException e1) {
						e1.printStackTrace();
					}
					url = URLqueue.geturl(timetime,task);//第二个队列，可用于扩展多线程，多进程，多机器执行
					if (url == null) {
						System.out.println("task:"+task.getId()+" 没有任务需要执行的url 等待");
						continue;
//						if () {
//							break;
//						}
					}
					//如果是目标URL，解析数据
					if (task.isTargetUrl(url.getUrl())){
						//(解析内容和解析URL倒底该如何分配工作才合理？？？？？？？？？？？？？？)
						//根据URL拿到内容
						String content = HttpTools.getContentFromUrlByGet(url.getUrl(), null, null, null);
						ParserI jiexiqi = task.getJiexiqi();
						//解析内容
						Map<String, Object> jiexicontent = jiexiqi.parseToMap(content);
						boolean success;
						if (MapUtils.isEmpty(jiexicontent)) {//解析不到内容，如何处理该链接
//							jiexiqi.chulisuccessurl(url,false,timetime);
							////////////////////////保存处理结果
							System.out.println("list null but url="+url.getUrl()+"");
							try {
								url.setTimetime(-1);
								url.save();
							} catch (Exception e) {
								System.out.println("URL状态保存异常");
								e.printStackTrace();
							}
							///////////////////////////////////////
							continue;
						} else {
							//保存解析出来的信息
							jiexiqi.runsaveinfo(url,jiexicontent);
							///////////////////////////////////保存处理结果
//							jiexiqi.chulisuccessurl(url,true,timetime);
							try {
								url.setTimetime(timetime);
								url.save();
							} catch (Exception e) {
								System.out.println("URL状态保存异常");
								e.printStackTrace();
							}
							/////////////////////////////////////
							//执行完毕
						}
						//解析URL（或者把这个工作扔给其它类，任务，或者线程）
						//投递新发现的URL，判断往哪个队列里投递
						//可以暂时不需要，对于一些指定的抓取，可以半人工半自动的方式，不需要获取全部URL？？？
//					URLgetter.geturls(content);
						//方式一解析新发现的分页URL??
						List<String> urls = jiexiqi.parsePages(content);
						//存储发现的新url
//						jiexiqi.savenewurls(url,urls);
						/////////////////////////////////
						if (CollectionUtils.isNotEmpty(urls)){
							for (String urll : urls) {
								String sql = "insert into unvisitedurl (`id_task`,`url`) values(" + task.getId() + ",'" + ParserTools.fixUrl(url, urll) + "')";
								try {
									Criteria c = new Criteria();
									c.add(UnvisitedurlPeer.URL, ParserTools.fixUrl(url, urll));
									List<Unvisitedurl> us = UnvisitedurlPeer.doSelect(c);
									if (CollectionUtils.isEmpty(us)) {
										BasePeer.executeStatement(sql);
									} else {
										
									}
								} catch (TorqueException e) {
									e.printStackTrace();
									System.out.println("插入数据库异常 sql:" + sql);
								}
							}
							//方式二找到翻页规则,找到最多有几页,更新url中的最大页数,然后根据最大页数遍历
						}
						//////////////////////////////////////////
					}
//					break;
				}
				/////////////////////这里保存任务执行状态
//				try {
//					task.setTimetime(timetime);
//					task.save();
//				} catch (Exception e) {
//					e.printStackTrace();
//					System.out.println("保存执行状态异常");
//				}
//				System.out.println("任务执行完成 task:"+task);
				///////////////////////////
			}
			try {
				Thread.sleep(sleeptime);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}
}
