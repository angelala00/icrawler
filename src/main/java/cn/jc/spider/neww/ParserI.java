package cn.jc.spider.neww;

import java.util.List;
import java.util.Map;

import cn.jc.spider.po.Unvisitedurl;

/**
 * ParserI目前能想到的可以有三种方式直接页面(两种实现方式，JSoup和正则，(能不能考虑用JS引擎来实现，貌似比JSoup更合适，这样就可以把JS代码放到数据库中，就可以动态的“教”系统怎么去做新的匹配了))，API类的JSON方式，API类的XML方式
 * StorerI目前能想到的有回调请求一个入库的接口方式(JSON，XML，或其它)，直接连接数据库入库方式(本地和远程)，输出到某一个输出流一种方式(本地文本等)
 * 
 * @author JiangChi
 *
 */
public interface ParserI {
	/**
	 * 解析成Map对象，里面嵌套有List等多层嵌套，看跟上面的方法合并一起
	 * @param content
	 * @return
	 */
	public Map<String, Object> parseToMap(String content);
	/**
	 * 解析分页的url	<中间页>
	 * @param content
	 * @return
	 */
	public List<String> parsePages(String content);
	/**
	 * 保存解析的目标数据
	 * @param url
	 * @param jiexicontent
	 */
	public void runsaveinfo(Unvisitedurl url, Map<String, Object> jiexicontent);

}
