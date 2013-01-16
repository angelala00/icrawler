package cn.jc.spider.po;


import org.apache.torque.om.Persistent;

import cn.jc.spider.neww.ParserI;
import cn.jc.spider.neww.StorerI;

/**
 * You should add additional methods to this class to meet the
 * application requirements.  This class will only be generated as
 * long as it does not already exist in the output directory.
 */
public  class Task
    extends cn.jc.spider.po.BaseTask
    implements Persistent
{
	private ParserI jiexiqi;
	private StorerI cunchuqi;
	public ParserI getJiexiqi() {
		return jiexiqi;
	}
	public void setJiexiqi(ParserI jiexiqi) {
		this.jiexiqi = jiexiqi;
	}
	public StorerI getCunchuqi() {
		return cunchuqi;
	}
	public void setCunchuqi(StorerI cunchuqi) {
		this.cunchuqi = cunchuqi;
	}

	/**
	 * 以后是否需要实现该方法？
	 * @param url
	 * @return
	 */
	public boolean isTargetUrl(String url) {
		return true;
	}
	@Override
	public String toString() {
		return "Task [id=" + super.getId() + ", jiexiqi=" + jiexiqi + ", cunchuqi="
				+ cunchuqi + "]";
	}
	
}
