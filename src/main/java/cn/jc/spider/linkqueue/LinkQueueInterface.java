package cn.jc.spider.linkqueue;


public interface LinkQueueInterface {

	public abstract void addVisitedUrl(String url);

	/**
	 * 加之前要判断一下是否存在
	 * @param url
	 */
	public abstract void addUnVisitedUrl(String url);

	public abstract int getVisitedUrlNum();
	
	public abstract int getUnVisitedUrlNum();

	public abstract Object unVisitedUrlDeQueue();

	public abstract boolean unVisitedUrlIsEmpty();


}