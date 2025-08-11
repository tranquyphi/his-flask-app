// Sign Template Details - Manage signs within a specific template
$(document).ready(function(){
  console.log('[SignTemplateDetails] Document ready - template ID:', TEMPLATE_ID);
  if($.ajaxSetup){ $.ajaxSetup({cache:false}); }
  
  const tableEl = $('#template-signs-table');
  const availableTableEl = $('#available-signs-table');
  
  let dt = null;
  let availableDt = null;
  let systemsCache = [];
  const addSignModal = new bootstrap.Modal(document.getElementById('addSignModal'));

  function loadSystems(){
    console.log('[SignTemplateDetails] Loading body systems...');
    return $.get('/api/body_system')
      .then(resp => {
        const list = resp.body_system || [];
        console.log('[SignTemplateDetails] Body systems fetched:', list.length);
        systemsCache = list;
        populateSystems(list);
        return list;
      })
      .catch(err => {
        console.error('[SignTemplateDetails] Error loading body systems:', err);
        return [];
      });
  }

  function populateSystems(list){
    const selectors = ['#filter-system', '#modal-filter-system'];
    selectors.forEach(selector => {
      const select = $(selector);
      select.empty().append('<option value="">Hệ cơ quan (tất cả)</option>');
      list.forEach(sys => {
        if(sys && sys.SystemId !== undefined){
          select.append(`<option value="${sys.SystemId}">${sys.SystemName || ('Hệ '+sys.SystemId)}</option>`);
        }
      });
    });
  }

  function loadTemplateInfo(){
    console.log('[SignTemplateDetails] Loading template info for ID:', TEMPLATE_ID);
    return $.get(`/api/sign-templates/${TEMPLATE_ID}`)
      .then(resp => {
        const template = resp.sign_template;
        $('#template-name').text(template.SignTemplateName);
        $('#template-id').text(template.SignTemplateId);
        console.log('[SignTemplateDetails] Template loaded:', template.SignTemplateName);
        return template;
      })
      .catch(err => {
        console.error('[SignTemplateDetails] Error loading template info:', err);
        showError('Không tải được thông tin mẫu');
        return null;
      });
  }

  function fetchTemplateSigns(){
    const params = {};
    const q = $('#search-desc').val().trim(); if(q) params.q = q;
    const type = $('#filter-type').val(); if(type !== '') params.type = type;
    const sys = $('#filter-system').val(); if(sys) params.system_id = sys;
    
    console.log('[SignTemplateDetails] Fetching template signs with params', params);
    params._ = Date.now();
    
    return $.get(`/api/sign-templates/${TEMPLATE_ID}/signs`, params)
      .then(resp => {
        console.log('[SignTemplateDetails] Template signs fetched:', resp.signs?.length || 0);
        return resp.signs || [];
      })
      .catch(err => {
        console.error('Error fetching template signs', err);
        showError('Không tải được dấu hiệu của mẫu');
        return [];
      });
  }

  function fetchAvailableSigns(){
    const params = {};
    const q = $('#modal-search').val().trim(); if(q) params.q = q;
    const type = $('#modal-filter-type').val(); if(type !== '') params.type = type;
    const sys = $('#modal-filter-system').val(); if(sys) params.system_id = sys;
    
    console.log('[SignTemplateDetails] Fetching available signs with params', params);
    params._ = Date.now();
    
    return $.get(`/api/sign-templates/${TEMPLATE_ID}/available-signs`, params)
      .then(resp => {
        console.log('[SignTemplateDetails] Available signs fetched:', resp.available_signs?.length || 0);
        return resp.available_signs || [];
      })
      .catch(err => {
        console.error('Error fetching available signs', err);
        showError('Không tải được danh sách dấu hiệu khả dụng');
        return [];
      });
  }

  function renderTemplateSigns(rows){
    console.log('[SignTemplateDetails] Rendering template signs table with:', rows.length, 'rows');
    if(dt){ dt.destroy(); tableEl.find('tbody').empty(); }
    
    dt = tableEl.DataTable({
      data: rows,
      columns: [
        {data:'SignId', title:'ID', visible:false},
        {data:'SignDesc', title:'Mô tả'},
        {
          data:'SignType', 
          title:'Loại', 
          render:(d)=> d?'<span class="badge bg-danger">Thực thể</span>':'<span class="badge bg-info text-dark">Cơ năng</span>'
        },
        {data:'SystemName', title:'Hệ', defaultContent:'N/A'},
        {data:'Speciality', title:'Chuyên khoa', defaultContent:''},
        {
          data:null, 
          title:'Thao tác', 
          orderable:false, 
          width:'80px', 
          render:(row)=> `
            <button class='btn btn-outline-danger btn-sm btn-remove' title='Loại bỏ' data-sign-id='${row.SignId}'>
              <i class='fas fa-times'></i>
            </button>`
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
        emptyTable: 'Chưa có dấu hiệu nào trong mẫu này',
        paginate: {previous:'Trước', next:'Tiếp'}
      }
    });
    
    $('#total-signs').text(rows.length);
    $('#debug-info').text('Template signs loaded: '+rows.length).show();
  }

  function renderAvailableSigns(rows){
    console.log('[SignTemplateDetails] Rendering available signs table with:', rows.length, 'rows');
    if(availableDt){ availableDt.destroy(); availableTableEl.find('tbody').empty(); }
    
    availableDt = availableTableEl.DataTable({
      data: rows,
      columns: [
        {data:'SignDesc', title:'Mô tả'},
        {
          data:'SignType', 
          title:'Loại', 
          render:(d)=> d?'<span class="badge bg-danger">Thực thể</span>':'<span class="badge bg-info text-dark">Cơ năng</span>'
        },
        {data:'SystemName', title:'Hệ', defaultContent:'N/A'},
        {data:'Speciality', title:'Chuyên khoa', defaultContent:''},
        {
          data:null, 
          title:'Thao tác', 
          orderable:false, 
          width:'80px', 
          render:(row)=> `
            <button class='btn btn-outline-success btn-sm btn-add-to-template' title='Thêm vào mẫu' data-sign-id='${row.SignId}'>
              <i class='fas fa-plus'></i>
            </button>`
        }
      ],
      pageLength: 10,
      order:[[0,'asc']],
      responsive:true,
      autoWidth:false,
      language:{
        search: 'Tìm:',
        lengthMenu: 'Hiển thị _MENU_',
        info: 'Hiển thị _START_ - _END_ / _TOTAL_',
        infoEmpty: '0 bản ghi',
        emptyTable: 'Không có dấu hiệu khả dụng',
        paginate: {previous:'Trước', next:'Tiếp'}
      }
    });
  }

  function refreshTemplateSigns(){
    $('#alert-container').empty();
    $('#debug-info').text('Fetching template signs...').show();
    
    fetchTemplateSigns().then(rows => {
      renderTemplateSigns(rows);
      if(rows.length === 0){
        showInfo('Chưa có dấu hiệu nào trong mẫu này.');
      }
    });
  }

  function refreshAvailableSigns(){
    fetchAvailableSigns().then(rows => {
      renderAvailableSigns(rows);
    });
  }

  // Event handlers
  $('#btn-add-sign').on('click', function(){
    refreshAvailableSigns();
    addSignModal.show();
  });

  $('#btn-refresh, #filter-type, #filter-system').on('click change', refreshTemplateSigns);
  $('#search-desc').on('keyup', debounce(refreshTemplateSigns, 400));

  $('#btn-modal-search, #modal-filter-type, #modal-filter-system').on('click change', refreshAvailableSigns);
  $('#modal-search').on('keyup', debounce(refreshAvailableSigns, 400));

  // Remove sign from template
  tableEl.on('click', '.btn-remove', function(){
    const signId = $(this).data('sign-id');
    const rowData = dt.row($(this).closest('tr')).data();
    if(!rowData) return;
    
    if(!confirm(`Loại bỏ dấu hiệu "${rowData.SignDesc}" khỏi mẫu này?`)) return;
    
    $.ajax({
      url: `/api/sign-templates/${TEMPLATE_ID}/signs/${signId}`,
      method: 'DELETE'
    })
    .done(()=> {
      refreshTemplateSigns();
      showSuccess('Đã loại bỏ dấu hiệu khỏi mẫu');
    })
    .fail(err=> {
      const errorMsg = err.responseJSON?.error || err.statusText || 'Lỗi không xác định';
      showError('Lỗi loại bỏ: ' + errorMsg);
    });
  });

  // Add sign to template
  availableTableEl.on('click', '.btn-add-to-template', function(){
    const signId = $(this).data('sign-id');
    const rowData = availableDt.row($(this).closest('tr')).data();
    if(!rowData) return;
    
    $.ajax({
      url: `/api/sign-templates/${TEMPLATE_ID}/signs`,
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({SignId: signId})
    })
    .done(()=> {
      refreshTemplateSigns();
      refreshAvailableSigns();
      showSuccess(`Đã thêm "${rowData.SignDesc}" vào mẫu`);
    })
    .fail(err=> {
      const errorMsg = err.responseJSON?.error || err.statusText || 'Lỗi không xác định';
      if(err.status === 409) {
        showError('Dấu hiệu này đã có trong mẫu rồi');
      } else {
        showError('Lỗi thêm dấu hiệu: ' + errorMsg);
      }
    });
  });

  // Initialize
  $('#debug-info').text('Initializing...').show();
  
  Promise.all([loadTemplateInfo(), loadSystems()])
    .then(() => {
      console.log('[SignTemplateDetails] Initialization complete, loading template signs');
      refreshTemplateSigns();
    })
    .catch(err => {
      console.error('[SignTemplateDetails] Initialization failed:', err);
      showError('Lỗi khởi tạo trang');
    });

  // Utility functions
  function debounce(fn, wait){ 
    let t; 
    return function(){ 
      const ctx=this, args=arguments; 
      clearTimeout(t); 
      t=setTimeout(()=>fn.apply(ctx,args), wait); 
    }; 
  }

  function showAlert(html, type){
    const id = 'alert-'+Date.now();
    $('#alert-container').append(`<div id='${id}' class='alert alert-${type} py-1 my-2'>${html}</div>`);
    setTimeout(()=> $('#'+id).fadeOut(400, function(){ $(this).remove(); }), 4000);
  }
  
  function showError(msg){ showAlert(`<i class='fas fa-exclamation-triangle me-1'></i>${msg}`,'danger'); }
  function showSuccess(msg){ showAlert(`<i class='fas fa-check-circle me-1'></i>${msg}`,'success'); }
  function showInfo(msg){ showAlert(`<i class='fas fa-info-circle me-1'></i>${msg}`,'info'); }
  
  window.__templateDetailsDebug = { 
    reload: refreshTemplateSigns, 
    templateData: ()=> dt?.data()?.toArray(),
    availableData: ()=> availableDt?.data()?.toArray()
  };
});
