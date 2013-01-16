package cn.jc.spider.linkqueue;

import java.util.HashSet;
import java.util.Set;

import org.apache.commons.lang.StringUtils;


/**
 * 队列
 * 
 * @author JiangChi
 * 
 */
public class LinkQueueMem implements LinkQueueInterface {

	/**
	 * 访问过的URL集合
	 */
	private Set<String> visitedUrl = new HashSet<String>();
	/**
	 * 未访问过的URL队列（目标URL）
	 */
	private Queue<String> unVisitedUrl = new Queue<String>();

	/* (non-Javadoc)
	 * @see cn.jc.spider.demo1.LinkQueueInterface#addVisitedUrl(java.lang.String)
	 */
	@Override
	public void addVisitedUrl(String url) {
		visitedUrl.add(url);
	}

	/* (non-Javadoc)
	 * @see cn.jc.spider.demo1.LinkQueueInterface#unVisitedUrlDeQueue()
	 */
	@Override
	public Object unVisitedUrlDeQueue() {
		return unVisitedUrl.deQueue();
	}

	/* (non-Javadoc)
	 * @see cn.jc.spider.demo1.LinkQueueInterface#addUnVisitedUrl(java.lang.String)
	 */
	@Override
	public void addUnVisitedUrl(String url) {
		if (StringUtils.isNotBlank(url) && !visitedUrl.contains(url)
				&& !unVisitedUrl.contains(url)) {
			unVisitedUrl.enQueue(url);
		}
	}

	/* (non-Javadoc)
	 * @see cn.jc.spider.demo1.LinkQueueInterface#getVisitedUrlNum()
	 */
	@Override
	public int getVisitedUrlNum() {
		return visitedUrl.size();
	}

	/* (non-Javadoc)
	 * @see cn.jc.spider.demo1.LinkQueueInterface#unVisitedUrlIsEmpty()
	 */
	@Override
	public boolean unVisitedUrlIsEmpty() {
		return unVisitedUrl.isQueueEmpty();
	}

	@Override
	public int getUnVisitedUrlNum() {
		// TODO Auto-generated method stub
		return 0;
	}
}
