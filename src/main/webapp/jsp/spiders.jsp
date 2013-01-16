<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>
<%
	String path = request.getContextPath();
	String basePath = request.getScheme() + "://"
			+ request.getServerName() + ":" + request.getServerPort()
			+ path + "/";
	pageContext.setAttribute("basePath", basePath);
	basePath = "";
	// System.out.println(basePath);
%>
<!DOCTYPE HTML>
<!-- <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"> -->
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>智能爬虫-beginning</title>
</head>

<body>
	<table>
		<tr><td>website</td><td>websiteurl</td><td>targeturlreg</td><td>unvisit</td><td>visit</td></tr>
		<c:forEach items="${crawlers }" var="crawler">
		<tr><td>${crawler.website.website }</td>
		<td>${crawler.website.websitesuperurl }</td>
		<td>${crawler.website.targetpageurlreg }</td>
		<td>${crawler.linkQueue.unVisitedUrlNum }</td>
		<td>${crawler.linkQueue.visitedUrlNum }</td></tr>
		</c:forEach>
	</table>
	<div class="window">
		<div class="screen">
			<div class="body">
			${num }
			</div>
			<!--body end-->
		</div>
		<!--screen end-->
	</div>
	<!--widnow end-->
</body>
<script type="text/javascript">
	
</script>
</html>