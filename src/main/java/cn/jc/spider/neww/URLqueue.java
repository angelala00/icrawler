package cn.jc.spider.neww;

import java.util.List;

import org.apache.commons.collections.CollectionUtils;
import org.apache.torque.TorqueException;
import org.apache.torque.util.Criteria;

import cn.jc.spider.po.Task;
import cn.jc.spider.po.Unvisitedurl;
import cn.jc.spider.po.UnvisitedurlPeer;

/**
 * @author JiangChi
 *
 */
public class URLqueue {

	/**
	 * 拿出该task的URL队列
	 * @param timetime 
	 * @param task
	 * @return
	 */
	public static Unvisitedurl geturl(int timetime, Task task) {
		Criteria c = new Criteria();
		c.add(UnvisitedurlPeer.ID_TASK, task.getId());
		c.add(UnvisitedurlPeer.TIMETIME, timetime, Criteria.NOT_EQUAL);
		c.addDescendingOrderByColumn(UnvisitedurlPeer.TIMETIME);
		c.setLimit(1);
		List<Unvisitedurl> us = null;
		try {
			us = UnvisitedurlPeer.doSelect(c);
		} catch (TorqueException e) {
			System.out.println("获取未访问的URL异常 sql:" + c.toString());
		}
		if (CollectionUtils.isEmpty(us)) {
			return null;
		} else {
			return us.get(0);
		}
	}

}
