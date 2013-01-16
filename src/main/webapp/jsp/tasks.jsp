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
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>task-CRUD</title>
<link rel="stylesheet" type="text/css" href="http://www.jeasyui.com/easyui/themes/default/easyui.css">
<link rel="stylesheet" type="text/css" href="http://www.jeasyui.com/easyui/themes/icon.css">
<link rel="stylesheet" type="text/css" href="http://www.jeasyui.com/easyui/demo/demo.css">
<script type="text/javascript" src="http://code.jquery.com/jquery-1.6.min.js"></script>
<script type="text/javascript" src="http://www.jeasyui.com/easyui/jquery.easyui.min.js"></script>
<script type="text/javascript" src="http://www.jeasyui.com/easyui/jquery.edatagrid.js"></script>
</head>

<body>
	<table id="dg" title="My Users" style="width:700px;height:250px"
			toolbar="#toolbar" pagination="true" idField="id"
			rownumbers="true" fitColumns="true" singleSelect="true">
		<thead>
			<tr>
				<th field="id" width="50" editor="text">id</th>
				<th field="name" width="50" editor="text">name</th>
				<th field="id_prior" width="50" editor="text">id_prior</th>
				<th field="id_next" width="50" editor="text">id_next</th>
				<th field="timetime" width="50" editor="text">timetime</th>
			</tr>
		</thead>
	</table>
	<div id="toolbar">
		<a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="javascript:$('#dg').edatagrid('addRow')">New</a>
		<a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="javascript:$('#dg').edatagrid('destroyRow')">Destroy</a>
		<a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-save" plain="true" onclick="javascript:$('#dg').edatagrid('saveRow')">Save</a>
		<a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-undo" plain="true" onclick="javascript:$('#dg').edatagrid('cancelRow')">Cancel</a>
	</div>

</body>
<script type="text/javascript">
	$(function(){
		$('#dg').edatagrid({
			url: '/icrawler/get_tasks.do',
			saveUrl: '/icrawler/save_task.do',
			updateUrl: '/icrawler/update_task.do',
			destroyUrl: '/icrawler/destroy_task.do'
		});
	});
</script>
</html>