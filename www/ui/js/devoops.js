/* jshint jquery: true */
/* jslint browser: true */

//
//    Main script of DevOOPS v1.0 Bootstrap Theme
//
"use strict";

var cinp;
var packrat;
var user;
var token;
var keepalive_interval;
var release_types = {};
var next_release = {};

/*-------------------------------------------
  Dynamically load plugin scripts
---------------------------------------------*/
//
//  Dynamically load Bootstrap Validator Plugin
//  homepage: https://github.com/nghuuphuoc/bootstrapvalidator
//
function LoadBootstrapValidatorScript(callback){
  if (!$.fn.bootstrapValidator){
    $.getScript('plugins/bootstrapvalidator/bootstrapValidator.min.js', callback);
  }
  else {
    if (callback && typeof(callback) === "function") {
      callback();
    }
  }
}
//
//  Dynamically load DataTables plugin
//  homepage: http://datatables.net v1.9.4 license - GPL or BSD
//
function loadDataTablesScripts(callback){
  function LoadDatatables(){
    $.getScript('plugins/datatables/jquery.dataTables.js', function(){
      $.getScript('plugins/datatables/ZeroClipboard.js', function(){
        $.getScript('plugins/datatables/TableTools.js', function(){
          $.getScript('plugins/datatables/dataTables.bootstrap.js', callback);
        });
      });
    });
  }
  if (!$.fn.dataTables){
    LoadDatatables();
  }
  else {
    if (callback && typeof(callback) === "function") {
      callback();
    }
  }
}
//
//  Dynamically load Springy plugin
//  homepage: http://getspringy.com/ 2.6.1 as is
//
function LoadSpringyScripts(callback){
  function LoadSpringyScript(){
    $.getScript('plugins/springy/springy.js', LoadSpringyUIScript);
  }
  function LoadSpringyUIScript(){
    $.getScript('plugins/springy/springyui.js', callback);
  }
  if (!$.fn.Springy){
    LoadSpringyScript();
  }
  else {
    if (callback && typeof(callback) === "function") {
      callback();
    }
  }
}
//
//  Dynamically load jQuery-Knob plugin
//  homepage: http://anthonyterrien.com/knob/  v1.2.5 License- MIT or GPL
//
function LoadKnobScripts(callback){
  if(!$.fn.knob){
    $.getScript('plugins/jQuery-Knob/jquery.knob.js', callback);
  }
  else {
    if (callback && typeof(callback) === "function") {
      callback();
    }
  }
}

/*-------------------------------------------
  Main scripts used by theme
---------------------------------------------*/
//
//  Function for load content from url and put in $('.ajax-content') block
//
function loadAjaxContent(url){
  $('.preloader').show();
  $.ajax({
    mimeType: 'text/html; charset=utf-8', // ! Need set mimeType only when run from local file
    url: url,
    type: 'GET',
    success: function(data) {
      $('#ajax-content').html(data);
      $('.preloader').hide();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      window.alert(errorThrown);
    },
    dataType: "html",
    async: false
  });
}
//
//  Function maked all .box selector is draggable, to disable for concrete element add class .no-drop
//
function WinMove(){
  $( "div.box").not('.no-drop')
    .draggable({
      revert: true,
      zIndex: 2000,
      cursor: "crosshair",
      handle: '.box-name',
      opacity: 0.8
    })
    .droppable({
      tolerance: 'pointer',
      drop: function( event, ui ) {
        var draggable = ui.draggable;
        var droppable = $(this);
        var dragPos = draggable.position();
        var dropPos = droppable.position();
        draggable.swap(droppable);
        setTimeout(function() {
          var dropmap = droppable.find('[id^=map-]');
          var dragmap = draggable.find('[id^=map-]');
          if (dragmap.length > 0 || dropmap.length > 0){
            dragmap.resize();
            dropmap.resize();
          }
          else {
            draggable.resize();
            droppable.resize();
          }
        }, 50);
        setTimeout(function() {
          draggable.find('[id^=map-]').resize();
          droppable.find('[id^=map-]').resize();
        }, 250);
      }
    });
}
//
// Swap 2 elements on page. Used by WinMove function
//
jQuery.fn.swap = function(b){
  b = jQuery(b)[0];
  var a = this[0];
  var t = a.parentNode.insertBefore(document.createTextNode(''), a);
  b.parentNode.insertBefore(a, b);
  t.parentNode.insertBefore(b, t);
  t.parentNode.removeChild(t);
  return this;
};
//
//  Function for create 2 dates in human-readable format (with leading zero)
//
function PrettyDates(){
  var currDate = new Date();
  var year = currDate.getFullYear();
  var month = currDate.getMonth() + 1;
  var startmonth = 1;
  if (month > 3){
    startmonth = month -2;
  }
  if (startmonth <=9){
    startmonth = '0'+startmonth;
  }
  if (month <= 9) {
    month = '0'+month;
  }
  var day= currDate.getDate();
  if (day <= 9) {
    day = '0'+day;
  }
  var startdate = year +'-'+ startmonth +'-01';
  var enddate = year +'-'+ month +'-'+ day;
  return [startdate, enddate];
}
//
//  Function set min-height of window (required for this theme)
//
function SetMinBlockHeight(elem){
  elem.css('min-height', window.innerHeight - 49);
}
//
//  Helper for correct size of Messages page
//
function MessagesMenuWidth(){
  var W = window.innerWidth;
  var W_menu = $('#sidebar-left').outerWidth();
  var w_messages = (W-W_menu)*16.666666666666664/100;
  $('#messages-menu').width(w_messages);
}
//
//  Helper for open ModalBox with requested header, content and bottom
//
//
function openModalBox(header, inner, bottom){
  var modalbox = $('#modalbox');
  modalbox.find('.modal-header-name span').html(header);
  modalbox.find('.devoops-modal-inner').html(inner);
  modalbox.find('.devoops-modal-bottom').html(bottom);
  modalbox.fadeIn('fast');
  $('body').addClass("body-expanded");
}
//
//  Close modalbox
//
//
function closeModalBox(){
  var modalbox = $('#modalbox');
  modalbox.fadeOut('fast', function(){
    modalbox.find('.modal-header-name span').children().remove();
    modalbox.find('.devoops-modal-inner').children().remove();
    modalbox.find('.devoops-modal-bottom').children().remove();
    $('body').removeClass("body-expanded");
  });
}
//
//  Beauty tables plugin (navigation in tables with inputs in cell)
//  Created by DevOOPS.
//
(function( $ ){
  $.fn.beautyTables = function() {
    var table = this;
    var string_fill = false;
    this.on('keydown', function(event) {
    var target = event.target;
    var tr = $(target).closest("tr");
    var col = $(target).closest("td");
    if (target.tagName.toUpperCase() == 'INPUT'){
      if (event.shiftKey === true){
        switch(event.keyCode) {
          case 37: // left arrow
            col.prev().children("input[type=text]").focus();
            break;
          case 39: // right arrow
            col.next().children("input[type=text]").focus();
            break;
          case 40: // down arrow
            if (string_fill===false){
              tr.next().find('td:eq('+col.index()+') input[type=text]').focus();
            }
            break;
          case 38: // up arrow
            if (string_fill===false){
              tr.prev().find('td:eq('+col.index()+') input[type=text]').focus();
            }
            break;
        }
      }
      if (event.ctrlKey === true){
        switch(event.keyCode) {
          case 37: // left arrow
            tr.find('td:eq(1)').find("input[type=text]").focus();
            break;
          case 39: // right arrow
            tr.find('td:last-child').find("input[type=text]").focus();
            break;
        case 40: // down arrow
          if (string_fill===false){
            table.find('tr:last-child td:eq('+col.index()+') input[type=text]').focus();
          }
          break;
        case 38: // up arrow
          if (string_fill===false){
            table.find('tr:eq(1) td:eq('+col.index()+') input[type=text]').focus();
          }
            break;
        }
      }
      if (event.keyCode == 13 || event.keyCode == 9 ) {
        event.preventDefault();
        col.next().find("input[type=text]").focus();
      }
      if (string_fill===false){
        if (event.keyCode == 34) {
          event.preventDefault();
          table.find('tr:last-child td:last-child').find("input[type=text]").focus();}
        if (event.keyCode == 33) {
          event.preventDefault();
          table.find('tr:eq(1) td:eq(1)').find("input[type=text]").focus();}
      }
    }
    });
    table.find("input[type=text]").each(function(){
      $(this).on('blur', function(event){
      var target = event.target;
      var col = $(target).parents("td");
      if(table.find("input[name=string-fill]").prop("checked")===true) {
        col.nextAll().find("input[type=text]").each(function() {
          $(this).val($(target).val());
        });
      }
    });
  });
};
})( jQuery );
//
// Beauty Hover Plugin (backlight row and col when cell in mouseover)
//
//
(function( $ ){
  $.fn.beautyHover = function() {
    var table = this;
    table.on('mouseover','td', function() {
      var idx = $(this).index();
      var rows = $(this).closest('table').find('tr');
      rows.each(function(){
        $(this).find('td:eq('+idx+')').addClass('beauty-hover');
      });
    })
    .on('mouseleave','td', function(e) {
      var idx = $(this).index();
      var rows = $(this).closest('table').find('tr');
      rows.each(function(){
        $(this).find('td:eq('+idx+')').removeClass('beauty-hover');
      });
    });
  };
})( jQuery );
//
//  Function convert values of inputs in table to JSON data
//
//
function Table2Json(table) {
  var result = {};
  table.find("tr").each(function () {
    var oneRow = [];
    var varname = $(this).index();
    $("td", this).each(function (index) { if (index !== 0) {oneRow.push($("input", this).val());}});
    result[varname] = oneRow;
  });
  var result_json = JSON.stringify(result);
  openModalBox('Table to JSON values', result_json);
}

function errorHandler( msg, stack_trace )
{
  openModalBox( msg, '<pre>' + stack_trace + '</pre>', '' );
}

/*-------------------------------------------
  Function for Packages (repos.html)
---------------------------------------------*/

function repoTable()
{
  if( $.fn.dataTable.isDataTable( '#repos-table' ) )
    return;

  $( '#repos-table' ).dataTable
  (
    {
      "aaSorting": [[ 0, "asc" ]],
      "sDom": "<'box-content'<'col-sm-6'f><'col-sm-6 text-right'l><'clearfix'>>rt<'box-content'<'col-sm-6'i><'col-sm-6 text-right'p><'clearfix'>>",
      "sPaginationType": "bootstrap",
      "oLanguage": {
        "sSearch": "",
        "sLengthMenu": '_MENU_'
      },
      "aaData": [],
      'aoColumns': [
        { 'title': 'Name', 'data': 'name' },
        { 'title': 'Description', 'data': 'description' },
        { 'title': 'Release', 'data': 'release_type_list' },
        { 'title': 'Manager', 'data': 'manager_type' },
        { 'title': 'Distros', 'data': 'distroversion_list' },
        { 'title': 'Created', 'data': 'created', 'type': 'date' },
        { 'title': 'Last Changed', 'data': 'updated' , 'type': 'date' },
        { 'title': 'uri' , 'data': 'uri', 'visible': false }
      ]
    }
  );

  loadRepos();
}

function loadRepos()
{
  var repos_table = $( '#repos-table' ).DataTable();

  $.when( packrat.getRepos() ).then(
    function( data )
    {
      repos_table.clear();
      for( var o in data )
      {
        var tmp = data[ o ];
        tmp.uri = o;
        repos_table.row.add( tmp );
      }
      repos_table.draw();
    }
  ).fail(
  function( reason )
  {
    window.alert( "failed to get repo list: (" + reason.code + "): " + reason.msg  );
  }
);

  repos_table.clear();
}

/*-------------------------------------------
  Function for Packages (mirrors.html)
---------------------------------------------*/

function mirrorTable()
{
  if( $.fn.dataTable.isDataTable( '#mirrors-table' ) )
    return;

  $( '#mirrors-table' ).dataTable
  (
    {
      "aaSorting": [[ 0, "asc" ]],
      "sDom": "<'box-content'<'col-sm-6'f><'col-sm-6 text-right'l><'clearfix'>>rt<'box-content'<'col-sm-6'i><'col-sm-6 text-right'p><'clearfix'>>",
      "sPaginationType": "bootstrap",
      "oLanguage": {
        "sSearch": "",
        "sLengthMenu": '_MENU_'
      },
      "aaData": [],
      'aoColumns': [
        { 'title': 'Description', 'data': 'description' },
        { 'title': 'Name', 'data': 'name' },
        { 'title': 'Repos', 'data': 'repo_list' },
        { 'title': 'Last Heartbeat', 'data': 'last_heartbeat', 'type': 'date' },
        { 'title': 'Last Changed', 'data': 'updated' , 'type': 'date' },
        { 'title': 'uri' , 'data': 'uri', 'visible': false }
      ]
    }
  );

  loadMirrors();
}

function loadMirrors()
{
  var mirrors_table = $( '#mirrors-table' ).DataTable();

  $.when( packrat.getMirrors() ).then(
    function( data )
    {
      mirrors_table.clear();
      for( var o in data )
      {
        var tmp = data[ o ];
        tmp.uri = o;
        mirrors_table.row.add( tmp );
      }
      mirrors_table.draw();
    }
  ).fail(
  function( reason )
  {
    window.alert( "failed to get mirror list: (" + reason.code + "): " + reason.msg  );
  }
);

  mirrors_table.clear();
}

/*-------------------------------------------
  Function for Packages (packages.html)
---------------------------------------------*/
function packageTable()
{
  if( $.fn.dataTable.isDataTable( '#packagefiles-table' ) )
    return;

  $( '#packagefiles-table' ).dataTable
  (
    {
      "aaSorting": [[ 0, "asc" ]],
      "sDom": "<'box-content'<'col-sm-6'f><'col-sm-6 text-right'l><'clearfix'>>rt<'box-content'<'col-sm-6'i><'col-sm-6 text-right'p><'clearfix'>>",
      "sPaginationType": "bootstrap",
      "oLanguage": {
        "sSearch": "",
        "sLengthMenu": '_MENU_'
      },
      "aaData": [],
      'aoColumns': [
        { 'title': 'Version', 'data': 'version' },
        { 'title': 'Distro Version', 'data': 'distroversion' },
        { 'title': 'Release', 'data': 'release' },
        { 'title': 'Created', 'data': 'created', 'type': 'date' },
        { 'title': 'Last Changed', 'data': 'updated' , 'type': 'date' },
        { 'title': 'Actions', 'data': null, 'target': -1, 'defaultContent': '<button action="promote" class="fa fa-level-up" title="Promote"></button> <button action="depr" class="fa fa-archive" title="Deprocate"></button>' },
        { 'title': 'uri' , 'data': 'uri', 'visible': false }
      ]
    }
  );

  var file_table = $( '#packagefiles-table' ).DataTable();

  $( '#packagefiles-table tbody' ).on( 'click', '[action="promote"]',
    function()
    {
      var row = file_table.row( $( this ).parents( 'tr' ) );
      var orig_data = row.data();
      var to;
      var cc_id;

      if( orig_data.release == '/api/v1/Repos/ReleaseType:depr:' )
      {
        window.alert( 'Can not promote a Deprocated File.' );
        return;
      }
      if( orig_data.release == '/api/v1/Repos/ReleaseType:prod:' )
      {
        return;
      }

      to = next_release[ orig_data.release ];
      if( to === undefined )
      {
        window.alert( 'Don\'t know how to promote from release "' + orig_data.release + '"' );
        return;
      }

      if( release_types[ to ].change_control_required )
      {
        cc_id = window.prompt( 'Please enter the Change Control Number' );
        if( !cc_id )
          return;
      }

      $.when( packrat.promote( orig_data.uri, to, cc_id ) ).then(
        function( data )
        {
          row.data( $.extend( {}, data.detail, { uri: orig_data.uri } ) ); // TODO: really should get the uri from the data.detail
        }
      ).fail(
        function( reason )
        {
          window.alert( 'Failed To Promote: ' + reason.msg );
        }
      );

    }
  );

  $( '#packagefiles-table tbody' ).on( 'click', '[action="depr"]',
    function()
    {
      var row = file_table.row( $( this ).parents( 'tr' ) );
      var orig_data = row.data();
      $.when( packrat.deprocate( orig_data.uri ) ).then(
        function( data )
        {
          row.data( $.extend( {}, data.detail, { uri: orig_data.uri } ) ); // TODO: really should get the uri from the data.detail
        }
      ).fail(
        function( reason )
        {
          window.alert( 'Failed To Deprocate: ' + reason.msg );
        }
      );
    }
  );
}

function loadPackageList()
{
  var packageMenu = $( '#messages-menu' );

  packageMenu.empty();

  $.when( packrat.getPackages() ).then(
    function( data )
    {
      for( var uri in data )
        packageMenu.append( '<li><a href="#" class="" id="package-2" uri="' + uri + '"><i class="fa fa-folder"></i><span class="hidden-xs">' + data[ uri ].name + '</span></a></li>' );

      packageMenu.append( '<li><a href="#" class="" id="add-package"><i class="fa fa-plus"></i><span class="hidden-xs">Add New Package</span></a></li>' );

      $( '#add-package' ).click( addPackage );
    }
  ).fail(
    function( reason )
    {
      window.alert( "failed to load Package List (" + reason.code + "): " + reason.msg );
    }
  );
}

function addPackage()
{
  var name = window.prompt( 'Package Name' );

  if( name === null )
  {
    window.alert( "Add Package Canceled" );
    return;
  }

  $.when( packrat.createPackage( name ) ).then(
    function( data )
    {
      window.alert( "Package created" );
      loadPackageList();
    }
  ).fail(
    function( reason )
    {
      window.alert( "Failed to Create Package (" + reason.code + "): " + reason.msg );
    }
  );
}

function loadPackageFiles( package_uri )
{
  var file_table = $( '#packagefiles-table' ).DataTable();

  file_table.clear();
  file_table.draw();

  $.when( packrat.getPackageFiles( package_uri ) ).then(
    function( data )
    {
      for( var o in data )
      {
        var tmp = data[ o ];
        tmp.uri = o;
        file_table.row.add( tmp );
      }
      file_table.draw();
    }
  ).fail(
    function( reason )
    {
      window.alert( "Failed to get Package Files (" + reason.code + "): " + reason.msg );
    }
  );
}

/*-------------------------------------------
  Function for Packages (addfile.html)
---------------------------------------------*/

function initUploader( fileInput, progBar, uploadedFile, fileSelectBtn, submitBtn, fileURI, errorMsg )
{
  progBar.hide();
  submitBtn.hide();
  uploadedFile.empty();

  fileSelectBtn.click(
    function()
    {
      fileInput.click();
    }
  );

  fileInput.fileupload(
    {
      dataType: 'json',
      singleFileUploads: true,
      autoUpload: false,
      //acceptFileTypes: /(\.|\/)(deb|rpm)$/i,
      done:
        function( e, data )
        {
          progBar.hide();
          uploadedFile.empty();
          uploadedFile.append( '<label>' + data.originalFiles[0].name + '</label>' );
          fileURI[0].value = data.result.uri;
          submitBtn.show();
          errorMsg.append( 'File Uploaded.' );
        },
      fail:
        function( e, data )
        {
          var result = data.jqXHR.responseJSON;
          errorHandler( result.msg, result.trace );
          progBar.hide();
          errorMsg.append( result.msg );
        },
      progressall:
        function( e, data )
        {
          progBar.show();
          var progress = parseInt( data.loaded / data.total * 100, 10 );
          progBar.css( 'width', progress + '%' );
          progBar.empty();
          progBar.append( '<span>' + progress + '% Complete</span>' );
        }
    }
  ).bind( 'fileuploadadd',
    function( e, data )
    {
      errorMsg.empty();

      //if( !data.originalFiles[0].name.match( /(\.|\/)(deb|rpm)$/i ) )
      //{
      //  window.alert( 'Must be a .deb or .rpm file.' );
      //  return;
      //}

      if( !window.confirm( 'Ok to upload file "' + data.originalFiles[0].name + '" of size "' + data.originalFiles[0].size + '"?' ) )
      {
        window.alert( 'Upload Canceled.' );
        return;
      }

      data.submit();
    }
  );

}

function initFileSaver( provenance, justification, distro, distro_select, fileURI, submitBtn, provenance_label, justification_label, file_label, distro_label, uploadedFile, errorMsg )
{
  distro_select.hide();

  submitBtn.click(
    function()
    {
      provenance_label.empty();
      justification_label.empty();
      file_label.empty();
      distro_label.empty();
      errorMsg.empty();
      $.when( packrat.addPackageFile( provenance[0].value, justification[0].value, fileURI[0].value, distro[0].value ) ).then(
        function( data )
        {
          if( Array.isArray( data.result.value ) )
          {
            errorMsg.append( 'Unable to Auto-Detect Distro, please select one.' );
            for( var val in data.result.value )
              distro.append( $( '<option></option>' ).attr( 'value', data.result.value[ val ] ).text( data.result.value[ val ] ) );
            distro_select.show();
          }
          else
          {
            submitBtn.hide();
            provenance[0].value = '';
            justification[0].value = '';
            fileURI[0].value = '';
            distro[0].value = '';
            distro.empty();
            uploadedFile.empty();
            distro_select.hide();
            errorMsg.append( 'New Packge File Added' );
          }
        }
      ).fail(
        function( reason )
        {
          if( reason.fields )
          {
            errorMsg.append( 'Fix the following field(s)' );
            if( reason.fields.provenance )
              provenance_label.append( reason.fields.provenance );
            if( reason.fields.justification )
              justification_label.append( reason.fields.justification );
            if( reason.fields.distro )
              distro_label.append( reason.fields.distro );
            if( reason.fields.file )
              file_label.append( reason.fields.file );
          }
          else
            errorMsg.append( reason.msg );
        }
      );
    }
  );
}

/*-------------------------------------------
  Function for Packages (index.html)
---------------------------------------------*/


function logout()
{
  $.removeCookie( 'user' );
  $.removeCookie( 'token' );

  $( '#user-logged-in' ).hide();
  $( '#user-logged-out' ).show();

  $( '#username' ).empty();

  clearInterval( keepalive_interval );

  cinp.setAuth( '', '' );

  packrat.logout( user, token );

  user = undefined;
  token = undefined;
}

//////////////////////////////////////////////////////
//////////////////////////////////////////////////////
//
//      MAIN DOCUMENT READY SCRIPT OF DEVOOPS THEME
//
//      In this script main logic of theme
//
//////////////////////////////////////////////////////
//////////////////////////////////////////////////////
$(document).ready(function () {
  $('body').on('click', '.show-sidebar', function (e) {
    e.preventDefault();
    $('div#main').toggleClass('sidebar-show');
    setTimeout(MessagesMenuWidth, 250);
  });
  var ajax_url = location.hash.replace(/^#/, '');
  if (ajax_url.length < 1) {
    ajax_url = 'home.html';
  }

  cinp = cinpBuilder();
  cinp.setHost( '' );
  cinp.on_server_error = errorHandler;

  packrat = packratBuilder( cinp );

  $.when( packrat.getReleaseTypes() ).then(
    function( data )
    {
      var release_indexes = [];
      var release_by_index = {};
      release_types = {};
      next_release = {};
      for( var key in data )
      {
        var object = data[ key ];
        release_by_index[ object.level ] = key;
        release_types[ key ] = object;
        release_indexes.push( object.level );
      }
      release_indexes.sort( function( a, b ) { return b - a; } );
      var prev = release_by_index[ release_indexes.shift() ];
      for( key in release_indexes )
      {
        var level = release_indexes[ key ];
        next_release[ release_by_index[ level ] ] = prev;
        prev = release_by_index[ level ];
      }
    }
  ).fail(
    function( reason )
    {
      window.alert( "Failed to get Release Types (" + reason.code + "): " + reason.msg );
    }
  );

  loadAjaxContent(ajax_url);
  $('.main-menu').on('click', 'a', function (e) {
    var parents = $(this).parents('li');
    var li = $(this).closest('li.dropdown');
    var another_items = $('.main-menu li').not(parents);
    another_items.find('a').removeClass('active');
    another_items.find('a').removeClass('active-parent');
    if ($(this).hasClass('dropdown-toggle') || $(this).closest('li').find('ul').length === 0) {
      $(this).addClass('active-parent');
      var current = $(this).next();
      if (current.is(':visible')) {
        li.find("ul.dropdown-menu").slideUp('fast');
        li.find("ul.dropdown-menu a").removeClass('active');
      }
      else {
        another_items.find("ul.dropdown-menu").slideUp('fast');
        current.slideDown('fast');
      }
    }
    else {
      if (li.find('a.dropdown-toggle').hasClass('active-parent')) {
        var pre = $(this).closest('ul.dropdown-menu');
        pre.find("li.dropdown").not($(this).closest('li')).find('ul.dropdown-menu').slideUp('fast');
      }
    }
    if ($(this).hasClass('active') === false) {
      $(this).parents("ul.dropdown-menu").find('a').removeClass('active');
      $(this).addClass('active');
    }
    if ($(this).hasClass('ajax-link')) {
      e.preventDefault();
      if ($(this).hasClass('add-full')) {
        $('#content').addClass('full-content');
      }
      else {
        $('#content').removeClass('full-content');
      }
      var url = $(this).attr('href');
      window.location.hash = url;
      loadAjaxContent(url);
    }
    if ($(this).attr('href') == '#') {
      e.preventDefault();
    }
  });
  var height = window.innerHeight - 49;
  $('#main').css('min-height', height)
    .on('click', '.expand-link', function (e) {
      var body = $('body');
      e.preventDefault();
      var box = $(this).closest('div.box');
      var button = $(this).find('i');
      button.toggleClass('fa-expand').toggleClass('fa-compress');
      box.toggleClass('expanded');
      body.toggleClass('body-expanded');
      var timeout = 0;
      if (body.hasClass('body-expanded')) {
        timeout = 100;
      }
      setTimeout(function () {
        box.toggleClass('expanded-padding');
      }, timeout);
      setTimeout(function () {
        box.resize();
        box.find('[id^=map-]').resize();
      }, timeout + 50);
    })
    .on('click', '.collapse-link', function (e) {
      e.preventDefault();
      var box = $(this).closest('div.box');
      var button = $(this).find('i');
      var content = box.find('div.box-content');
      content.slideToggle('fast');
      button.toggleClass('fa-chevron-up').toggleClass('fa-chevron-down');
      setTimeout(function () {
        box.resize();
        box.find('[id^=map-]').resize();
      }, 50);
    })
    .on('click', '.close-link', function (e) {
      e.preventDefault();
      var content = $(this).closest('div.box');
      content.remove();
    });
  $('body').on('click', 'a.close-link', function(e){
    e.preventDefault();
    closeModalBox();
  });
  $('#top-panel').on('click','a', function(e){
    if ($(this).hasClass('ajax-link')) {
      e.preventDefault();
      if ($(this).hasClass('add-full')) {
        $('#content').addClass('full-content');
      }
      else {
        $('#content').removeClass('full-content');
      }
      var url = $(this).attr('href');
      window.location.hash = url;
      loadAjaxContent(url);
    }
  });

  user = $.cookie( 'user' );
  token = $.cookie( 'token' );

  if( user )
  {
    $( '#user-logged-out' ).hide();
    $( '#username' ).empty();
    $( '#username' ).append( user );
    cinp.setAuth( user, token );
    keepalive_interval = setInterval(
      function()
      {
        packrat.keepalive();
      }, 60000 );
  }
  else
    $( '#user-logged-in' ).hide();

  $( '#doLogout' ).click( logout );
});
