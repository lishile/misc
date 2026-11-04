<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">


<html class="ui-mobile">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta name="viewport"
	content="target-densitydpi=get-target-densitydpi, width=device-width, initial-scale=1, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
<title>${companyName}</title>

<link href="https://misc.lishile.dpdns.org/seedcssjs/css/jquery.mobile-1.4.5.css"
	rel="stylesheet" type="text/css">
<link href="https://misc.lishile.dpdns.org/seedcssjs/css/skyd.css" rel="stylesheet"
	type="text/css">
<link href="https://misc.lishile.dpdns.org/seedcssjs/css/jquery.mobile.icons.min.css"
	rel="stylesheet" type="text/css">
<script src="https://misc.lishile.dpdns.org/seedcssjs/css/jquery.min.js"
	type="text/javascript"></script>
<script src="https://misc.lishile.dpdns.org/seedcssjs/css/jquery.mobile-1.4.5.min.js"
	type="text/javascript"></script>

<script type="text/javascript">
	$(document).ready(function() {

	});
</script>
</head>

<body class="ui-mobile-viewport ui-overlay-e">

	<div data-role="page" id="index" data-theme="e" data-url="index"
		tabindex="0"
		class="ui-page ui-page-theme-e ui-page-header-fixed ui-page-footer-fixed ui-page-active"
		style="padding-top: 44px; padding-bottom: 37px; min-height: 469px;">
		<div data-role="header" data-position="fixed" role="banner"
			class="ui-header ui-bar-inherit ui-header-fixed slidedown ui-fixed-hidden">
			<h1 class="ui-title" role="heading" aria-level="1">公主岭市松辽农业科学研究所</h1>
		</div>
		<div role="main" class="ui-content">
			<ul data-role="listview" data-inset="true" data-theme="h"
				class="ui-listview ui-listview-inset ui-corner-all ui-shadow ui-group-theme-h">
				<li data-role="list-divider" role="heading"
					class="ui-li-divider ui-bar-h ui-li-has-count ui-first-child">
					生产信息</li>

				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h1 style="white-space:normal;">
						<strong><font color="red">生产日期：</font>${date}</strong>
					</h1>
				</li>
				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h1 style="white-space:normal;">
						<strong><font color="red">检测日期：</font>${date2}</strong>
					</h1>
				</li>
				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h1 style="white-space:normal;">
						<strong><font color="red">加工批次：</font>${no}</strong>
					</h1>
				</li>

			</ul>

		</div>

		<div role="main" class="ui-content">
			<ul data-role="listview" data-inset="true" data-theme="h"
				class="ui-listview ui-listview-inset ui-corner-all ui-shadow ui-group-theme-h">
				<li data-role="list-divider" role="heading"
					class="ui-li-divider ui-bar-h ui-li-has-count ui-first-child">
					物流及经销商信息</li>

				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h3 style="white-space:normal;">
						<strong><font color="red">物流信息：</font>${transfer}</strong>
					</h3>
				</li>
				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h3 style="white-space:normal;">
						<strong><font color="red">产地：</font>公主岭</strong>
					</h3>
				</li>
				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h3 style="white-space:normal;">
						<strong><font color="red">经销商：</font>${jingxiaoshang}</strong>
					</h3>
				</li>

			</ul>

		</div>
		
		
		<div role="main" class="ui-content">
			<ul data-role="listview" data-inset="true" data-theme="h"
				class="ui-listview ui-listview-inset ui-corner-all ui-shadow ui-group-theme-h">
				<li data-role="list-divider" role="heading"
					class="ui-li-divider ui-bar-h ui-li-has-count ui-first-child">
					检验加工信息</li>
				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h3 style="white-space:normal;">
						<strong><font color="red">检验员信息：</font>吉种企检字第220441号</strong>
					</h3>
				</li>
				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h3 style="white-space:normal;">
						<strong><font color="red">加工员信息：</font>（吉）种加工字第20127126号</strong>
					</h3>
				</li>
			</ul>
		</div>

		<div role="main" class="ui-content">
			<ul data-role="listview" data-inset="true" data-theme="h"
				class="ui-listview ui-listview-inset ui-corner-all ui-shadow ui-group-theme-h">
				<li data-role="list-divider" role="heading"
					class="ui-li-divider ui-bar-h ui-li-has-count ui-first-child">
					品种信息</li>
				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h3 style="white-space:normal;">
						<strong><font color="red">品种名称：</font>${pinzhongName}</strong>
					</h3>
				</li>
				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h3 style="white-space:normal;">
						<strong><font color="red">审定编号：</font>${shendingbianhao}</strong>
					</h3>
				</li>
				
			</ul>
		</div>
		
<div role="main" class="ui-content">
			<ul data-role="listview" data-inset="true" data-theme="h"
				class="ui-listview ui-listview-inset ui-corner-all ui-shadow ui-group-theme-h">
				<li data-role="list-divider" role="heading"
					class="ui-li-divider ui-bar-h ui-li-has-count ui-first-child">
					风险提示</li>

				<li class="ui-li-static ui-body-inherit ui-last-child">
					<h3 style="white-space:normal;">
						<strong><font color="red">建议进行种子浸种消毒,浸种时加入防治杆尖线虫病药剂浸种</font></strong>
					</h3>
				</li>
				 
			</ul>

		</div>
		<div data-role="footer" data-position="fixed" role="contentinfo"
			class="ui-footer ui-bar-inherit ui-footer-fixed slideup ui-fixed-hidden">
			<div
				style="font-size: 12px; height: 25px; padding-top: 10px; text-align: center">${companyName}</div>
		</div>
	</div>



</body>
</html>
