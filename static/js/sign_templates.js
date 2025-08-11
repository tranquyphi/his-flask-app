// Sign Templates CRUD & listing
$(document).ready(function(){
  console.log('[SignTemplates] Document ready - script version 1.0');
  if($.ajaxSetup){ $.ajaxSetup({cache:false}); }
  
  const tableEl = $('#templates-table');
  if(!tableEl.length){ console.error('[SignTemplates] Table element #templates-table not found'); return; }
  if(!$.fn.DataTable){ console.error('[SignTemplates] DataTables plugin not loaded'); }
  
  let dt = null;
  let departmentsCache = [];
  const modalEl = new bootstrap.Modal(document.getElementById('templateModal'));

  function loadDepartments(){
    console.log('[SignTemplates] Loading departments...');
    return $.get('/api/department')
      .then(resp => {
        const list = resp.department || [];
        console.log('[SignTemplates] Departments fetched:', list.length);
        departmentsCache = list;
        populateDepartments(list);
        return list;
      })
      .catch(err => {
        console.error('[SignTemplates] Error loading departments:', err);
        showError('Không tải được danh sách khoa');
        return [];
      });
  }

  function populateDepartments(list){
    const filterSelect = $('#filter-department');
    const formSelect = $('#DepartmentId');
    
    filterSelect.empty().append('<option value="">Khoa (tất cả)</option>');
    formSelect.empty().append('<option value="">Chọn khoa</option>');
    
    list.forEach(dept => {
      if(dept && dept.DepartmentId !== undefined){
        const option = `<option value="${dept.DepartmentId}">${dept.DepartmentName || ('Khoa '+dept.DepartmentId)}</option>`;
        filterSelect.append(option);
        formSelect.append(option);
      }
    });
  }

  function fetchData(){
    const params = {};
    const q = $('#search-name').val().trim(); if(q) params.q = q;
    const dept = $('#filter-department').val(); if(dept) params.department_id = dept;
    const type = $('#filter-type').val(); if(type) params.template_type = type;
    
    console.log('Fetching /api/sign-templates with params', params);
    params._ = Date.now();
    
    return $.get('/api/sign-templates', params)
      .then(resp => {
        if(!resp || typeof resp !== 'object'){
          console.warn('[SignTemplates] Unexpected response', resp);
        }
        let rows = (resp && resp.sign_templates) || [];
        console.log('[SignTemplates] Fetched:', rows.length, 'templates');
        return rows;
      })
      .catch(err => {
        console.error('Error fetching /api/sign-templates', err);
        showError('Không tải được dữ liệu mẫu dấu hiệu');
        return [];
      });
  }

  function renderTable(rows){
    console.log('[SignTemplates] Rendering table with rows:', rows.length);
    if(dt){ dt.destroy(); tableEl.find('tbody').empty(); }
    
    dt = tableEl.DataTable({
      data: rows,
      columns: [
        {data:'SignTemplateId', title:'ID', visible:false},
        {data:'SignTemplateName', title:'Tên mẫu'},
        {data:'DepartmentName', title:'Khoa', defaultContent:'N/A'},
        {
          data:'SignTemplateType', 
          title:'Loại',
          render: function(data) {
            const typeMap = {
              'BA': '<span class="badge bg-primary">Bệnh án</span>',
              'TD': '<span class="badge bg-success">Tự động</span>',
              'PK': '<span class="badge bg-info">Phòng khám</span>',
              'CC': '<span class="badge bg-warning text-dark">Cấp cứu</span>'
            };
            return typeMap[data] || `<span class="badge bg-secondary">${data}</span>`;
          }
        },
        {
          data:null, 
          title:'Thao tác', 
          orderable:false, 
          width:'120px', 
          render:(row)=> `
            <div class='btn-group btn-group-sm'>
              <button class='btn btn-outline-primary btn-details' title='Chi tiết dấu hiệu' data-id='${row.SignTemplateId}'>
                <i class='fas fa-list'></i>
              </button>
              <button class='btn btn-outline-success btn-edit' title='Sửa' data-id='${row.SignTemplateId}'>
                <i class='fas fa-edit'></i>
              </button>
              <button class='btn btn-outline-danger btn-del' title='Xóa' data-id='${row.SignTemplateId}'>
                <i class='fas fa-trash'></i>
              </button>
            </div>`
        }
      ],
      pageLength: 25,
      order:[[1,'asc']],
      responsive:true,
      autoWidth:false,
      language:{
        search: 'Tìm:',
        lengthMenu: 'Hiển thị _MENU_',
        info: 'Hiển thị _START_ - _END_ / _TOTAL_',
        infoEmpty: '0 bản ghi',
        emptyTable: 'Không có mẫu dấu hiệu nào',
        paginate: {previous:'Trước', next:'Tiếp'}
      }
    });
    
    console.log('[SignTemplates] DataTable initialized');
    $('#templates-debug').text('Loaded templates: '+rows.length).show();
  }

  function refresh(){
    $('#alert-container').empty();
    $('#templates-debug').text('Fetching data...').show();
    
    fetchData().then(rows => {
      renderTable(rows);
      if(rows.length === 0){
        showInfo('Không có mẫu dấu hiệu phù hợp bộ lọc.');
      }
    }).catch(err => showError('Lỗi tải dữ liệu: '+ (err?.responseJSON?.error || err?.statusText || err)));
  }

  function clearForm(){
    $('#SignTemplateId').val('');
    $('#SignTemplateName').val('');
    $('#DepartmentId').val('');
    $('#SignTemplateType').val('TD');
  }

  // Event handlers
  $('#btn-add-template').on('click', function(){
    clearForm();
    $('#modalTitle').text('Thêm mẫu dấu hiệu');
    modalEl.show();
  });

  function debounce(fn, wait){ 
    let t; 
    return function(){ 
      const ctx=this, args=arguments; 
      clearTimeout(t); 
      t=setTimeout(()=>fn.apply(ctx,args), wait); 
    }; 
  }
  
  $('#btn-refresh, #filter-department, #filter-type').on('click change', refresh);
  $('#search-name').on('keyup', debounce(refresh, 400));

  // Save template
  $('#btn-save-template').on('click', function(){
    const payload = {
      SignTemplateName: $('#SignTemplateName').val().trim(),
      DepartmentId: $('#DepartmentId').val(),
      SignTemplateType: $('#SignTemplateType').val()
    };
    
    if(!payload.SignTemplateName){ alert('Tên mẫu bắt buộc'); return; }
    if(!payload.DepartmentId){ alert('Chọn khoa'); return; }
    if(!payload.SignTemplateType){ alert('Chọn loại mẫu'); return; }
    
    const id = $('#SignTemplateId').val();
    const method = id? 'PUT':'POST';
    const url = id? `/api/sign-templates/${id}`:'/api/sign-templates';
    
    $.ajax({
      url, 
      method, 
      contentType:'application/json', 
      data: JSON.stringify(payload)
    })
    .done(()=>{ 
      modalEl.hide(); 
      refresh(); 
      showSuccess(id ? 'Cập nhật mẫu thành công' : 'Tạo mẫu mới thành công');
    })
    .fail(err=> {
      const errorMsg = err.responseJSON?.error || err.statusText || 'Lỗi không xác định';
      showError('Lỗi lưu: ' + errorMsg);
    });
  });

  // Table row actions
  tableEl.on('click', '.btn-details', function(){
    const templateId = $(this).data('id');
    console.log('[SignTemplates] Opening details for template:', templateId);
    window.location.href = `/sign-templates/${templateId}/details`;
  });

  tableEl.on('click', '.btn-edit', function(){
    const templateId = $(this).data('id');
    const rowData = dt.row($(this).closest('tr')).data();
    if(!rowData) return;
    
    $('#SignTemplateId').val(rowData.SignTemplateId);
    $('#SignTemplateName').val(rowData.SignTemplateName);
    $('#DepartmentId').val(rowData.DepartmentId);
    $('#SignTemplateType').val(rowData.SignTemplateType);
    $('#modalTitle').text('Cập nhật mẫu dấu hiệu');
    modalEl.show();
  });

  tableEl.on('click', '.btn-del', function(){
    const templateId = $(this).data('id');
    const rowData = dt.row($(this).closest('tr')).data();
    if(!rowData) return;
    
    if(!confirm(`Xóa mẫu "${rowData.SignTemplateName}"?\nLưu ý: Điều này sẽ xóa tất cả dấu hiệu liên quan đến mẫu này.`)) return;
    
    $.ajax({
      url:`/api/sign-templates/${templateId}`, 
      method:'DELETE'
    })
    .done(()=> {
      refresh();
      showSuccess('Xóa mẫu thành công');
    })
    .fail(err=> {
      const errorMsg = err.responseJSON?.error || err.statusText || 'Lỗi không xác định';
      showError('Lỗi xóa: ' + errorMsg);
    });
  });

  // Initialize
  $('#templates-debug').text('Initializing...').show();
  loadDepartments().then(()=>{
    console.log('[SignTemplates] Departments loaded, starting refresh');
    refresh();
  });

  // Utility functions
  function showAlert(html, type){
    const id = 'alert-'+Date.now();
    $('#alert-container').append(`<div id='${id}' class='alert alert-${type} py-1 my-2'>${html}</div>`);
    setTimeout(()=> $('#'+id).fadeOut(400, function(){ $(this).remove(); }), 4000);
  }
  
  function showError(msg){ showAlert(`<i class='fas fa-exclamation-triangle me-1'></i>${msg}`,'danger'); }
  function showSuccess(msg){ showAlert(`<i class='fas fa-check-circle me-1'></i>${msg}`,'success'); }
  function showInfo(msg){ showAlert(`<i class='fas fa-info-circle me-1'></i>${msg}`,'info'); }
  
  window.__signTemplatesDebug = { reload: refresh, data: ()=> dt?.data()?.toArray() };
});
