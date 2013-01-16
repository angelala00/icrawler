package cn.jc.spider.linkqueue;

import java.util.LinkedList;

/**
 * 一个队列
 * 
 * @author JiangChi
 *
 */
public class Queue<T> {

	private LinkedList<T> queue = new LinkedList<T>();
	public void enQueue(T o){
		queue.add(o);
	}
	public T deQueue(){
		return queue.removeFirst();
	}
	public boolean isQueueEmpty(){
		return queue.isEmpty();
	}
	public boolean contains(T o){
		return queue.contains(o);
	}
}
