// Drug Template Details - Manage drugs within a specific template
$(document).ready(function(){
  console.log('[DrugTemplateDetails] Document ready - template ID:', TEMPLATE_ID);
  if($.ajaxSetup){ $.ajaxSetup({cache:false}); }
  
  const tableEl = $('#template-drugs-table');
  const availableTableEl = $('#available-drugs-table');
  
  let dt = null;
  let availableDt = null;
  let groupsCache = [];
  let formulationCache = [];
  const addDrugModal = new bootstrap.Modal(document.getElementById('addDrugModal'));

  function loadDrugGroups(){
    console.log('[DrugTemplateDetails] Loading drug groups...');
    return $.get('/api/drug-groups')
      .then(resp => {
        const list = resp.drug_groups || [];
        console.log('[DrugTemplateDetails] Drug groups fetched:', list.length);
        groupsCache = list;
        populateGroups(list);
        return list;
      })
      .catch(err => {
        console.error('[DrugTemplateDetails] Error loading drug groups:', err);
        return [];
      });
  }

  function populateGroups(list){
    const selectors = ['#filter-group', '#modal-filter-group'];
    selectors.forEach(selector => {
      const select = $(selector);
      select.empty().append('<option value="">Nhóm (tất cả)</option>');
      list.forEach(group => {
        if(group && group.DrugGroupId !== undefined){
          select.append(`<option value="${group.DrugGroupId}">${group.DrugGroupName || ('Nhóm '+group.DrugGroupId)}</option>`);
        }
      });
    });
  }

  function loadFormulations(){
    console.log('[DrugTemplateDetails] Loading formulations from drugs...');
    return $.get('/api/drugs')
      .then(resp => {
        const drugs = resp.drugs || [];
        const formulations = [...new Set(drugs.map(d => d.DrugFormulation).filter(f => f))].sort();
        console.log('[DrugTemplateDetails] Formulations extracted:', formulations.length);
        formulationCache = formulations;
        populateFormulations(formulations);
        return formulations;
      })
      .catch(err => {
        console.error('[DrugTemplateDetails] Error loading formulations:', err);
        return [];
      });
  }

  function populateFormulations(list){
    const selectors = ['#filter-formulation', '#modal-filter-formulation'];
    selectors.forEach(selector => {
      const select = $(selector);
      select.empty().append('<option value="">Dạng (tất cả)</option>');
      list.forEach(formulation => {
        select.append(`<option value="${formulation}">${formulation}</option>`);
      });
    });
  }

  function loadTemplateInfo(){
    console.log('[DrugTemplateDetails] Loading template info for ID:', TEMPLATE_ID);
    return $.get(`/api/drug-templates/${TEMPLATE_ID}`)
      .then(resp => {
        const template = resp.drug_template;
        $('#template-name').text(template.DrugTemplateName);
        $('#template-id').text(template.DrugTemplateId);
        $('#department-name').text(template.DepartmentName || 'N/A');
        console.log('[DrugTemplateDetails] Template loaded:', template.DrugTemplateName);
        return template;
      })
      .catch(err => {
        console.error('[DrugTemplateDetails] Error loading template:', err);
        showError('Không thể tải thông tin mẫu thuốc');
        throw err;
      });
  }

  function fetchTemplateDrugs(){
    const params = new URLSearchParams();
    const searchName = $('#search-name').val();
    const filterGroup = $('#filter-group').val();
    const filterAvailable = $('#filter-available').val();
    const filterFormulation = $('#filter-formulation').val();
    
    if(searchName) params.append('drug_name', searchName);
    if(filterGroup) params.append('drug_group_id', filterGroup);
    if(filterAvailable) params.append('available', filterAvailable);
    if(filterFormulation) params.append('formulation', filterFormulation);
    
    const url = `/api/drug-templates/${TEMPLATE_ID}/drugs?${params.toString()}`;
    console.log('[DrugTemplateDetails] Fetching template drugs from:', url);
    
    return $.get(url)
      .then(resp => {
        const drugs = resp.drugs || [];
        console.log('[DrugTemplateDetails] Template drugs fetched:', drugs.length);
        return drugs;
      })
      .catch(err => {
        console.error('[DrugTemplateDetails] Error fetching template drugs:', err);
        showError('Lỗi tải danh sách thuốc trong mẫu');
        return [];
      });
  }

  function fetchAvailableDrugs(){
    const params = new URLSearchParams();
    const modalSearch = $('#modal-search').val();
    const modalGroup = $('#modal-filter-group').val();
    const modalAvailable = $('#modal-filter-available').val();
    const modalFormulation = $('#modal-filter-formulation').val();
    
    if(modalSearch) params.append('drug_name', modalSearch);
    if(modalGroup) params.append('drug_group_id', modalGroup);
    if(modalAvailable) params.append('available', modalAvailable);
    if(modalFormulation) params.append('formulation', modalFormulation);
    
    const url = `/api/drugs?${params.toString()}`;
    console.log('[DrugTemplateDetails] Fetching available drugs from:', url);
    
    return $.get(url)
      .then(resp => {
        const drugs = resp.drugs || [];
        console.log('[DrugTemplateDetails] Available drugs fetched:', drugs.length);
        return drugs;
      })
      .catch(err => {
        console.error('[DrugTemplateDetails] Error fetching available drugs:', err);
        showError('Lỗi tải danh sách thuốc có sẵn');
        return [];
      });
  }

  function renderTemplateDrugs(rows){
    console.log('[DrugTemplateDetails] Rendering template drugs table with:', rows.length, 'rows');
    if(dt){ dt.destroy(); tableEl.find('tbody').empty(); }
    
    dt = tableEl.DataTable({
      data: rows,
      columns: [
        {data:'DrugId', title:'ID', visible:false},
        {data:'DrugName', title:'Tên thuốc'},
        {data:'DrugGenericName', title:'Tên hóa học', defaultContent:''},
        {data:'DrugGroupName', title:'Nhóm', defaultContent:'N/A'},
        {data:'DrugFormulation', title:'Dạng bào chế', defaultContent:''},
        {
          data:'DrugAvailable', 
          title:'Tình trạng', 
          render:(d)=> d?'<span class="badge bg-success">Có sẵn</span>':'<span class="badge bg-warning text-dark">Hết hàng</span>'
        },
        {
          data:null, 
          title:'Thao tác', 
          orderable:false, 
          width:'80px', 
          render:(row)=> `
            <button class='btn btn-outline-danger btn-sm btn-remove' title='Loại bỏ' data-drug-id='${row.DrugId}'>
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
        emptyTable: 'Chưa có thuốc nào trong mẫu này',
        paginate: {previous:'Trước', next:'Tiếp'}
      }
    });
    
    $('#total-drugs').text(rows.length);
    $('#debug-info').text('Template drugs loaded: '+rows.length).show();
  }

  function renderAvailableDrugs(rows){
    console.log('[DrugTemplateDetails] Rendering available drugs table with:', rows.length, 'rows');
    if(availableDt){ availableDt.destroy(); availableTableEl.find('tbody').empty(); }
    
    availableDt = availableTableEl.DataTable({
      data: rows,
      columns: [
        {data:'DrugName', title:'Tên thuốc'},
        {data:'DrugGenericName', title:'Tên hóa học', defaultContent:''},
        {data:'DrugGroupName', title:'Nhóm', defaultContent:'N/A'},
        {data:'DrugFormulation', title:'Dạng bào chế', defaultContent:''},
        {
          data:'DrugAvailable', 
          title:'Tình trạng', 
          render:(d)=> d?'<span class="badge bg-success">Có sẵn</span>':'<span class="badge bg-warning text-dark">Hết hàng</span>'
        },
        {
          data:null, 
          title:'Thao tác', 
          orderable:false, 
          width:'80px', 
          render:(row)=> `
            <button class='btn btn-outline-success btn-sm btn-add-to-template' title='Thêm vào mẫu' data-drug-id='${row.DrugId}'>
              <i class='fas fa-plus'></i>
            </button>`
        }
      ],
      pageLength: 10,
      order:[[0,'asc']],
      responsive:true,
      autoWidth:false,
      searching:false,
      language:{
        lengthMenu: 'Hiển thị _MENU_',
        info: 'Hiển thị _START_ - _END_ / _TOTAL_',
        infoEmpty: '0 bản ghi',
        emptyTable: 'Không tìm thấy thuốc nào',
        paginate: {previous:'Trước', next:'Tiếp'}
      }
    });
  }

  function refreshTemplateDrugs(){
    fetchTemplateDrugs().then(rows => {
      renderTemplateDrugs(rows);
    });
  }

  function refreshAvailableDrugs(){
    fetchAvailableDrugs().then(rows => {
      renderAvailableDrugs(rows);
    });
  }

  // Event handlers
  $('#btn-add-drug').on('click', function(){
    refreshAvailableDrugs();
    addDrugModal.show();
  });

  $('#btn-refresh, #filter-group, #filter-available, #filter-formulation').on('click change', refreshTemplateDrugs);
  $('#search-name').on('keyup', debounce(refreshTemplateDrugs, 400));

  $('#btn-modal-search, #modal-filter-group, #modal-filter-available, #modal-filter-formulation').on('click change', refreshAvailableDrugs);
  $('#modal-search').on('keyup', debounce(refreshAvailableDrugs, 400));

  // Remove drug from template
  tableEl.on('click', '.btn-remove', function(){
    const drugId = $(this).data('drug-id');
    const rowData = dt.row($(this).closest('tr')).data();
    if(!rowData) return;
    
    if(!confirm(`Loại bỏ thuốc "${rowData.DrugName}" khỏi mẫu này?`)) return;
    
    $.ajax({
      url: `/api/drug-templates/${TEMPLATE_ID}/drugs/${drugId}`,
      method: 'DELETE'
    })
    .done(()=> {
      refreshTemplateDrugs();
      showSuccess('Đã loại bỏ thuốc khỏi mẫu');
    })
    .fail(err=> {
      const errorMsg = err.responseJSON?.error || err.statusText || 'Lỗi không xác định';
      showError('Lỗi loại bỏ: ' + errorMsg);
    });
  });

  // Add drug to template
  availableTableEl.on('click', '.btn-add-to-template', function(){
    const drugId = $(this).data('drug-id');
    const rowData = availableDt.row($(this).closest('tr')).data();
    if(!rowData) return;
    
    $.ajax({
      url: `/api/drug-templates/${TEMPLATE_ID}/drugs`,
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({DrugId: drugId})
    })
    .done(()=> {
      refreshTemplateDrugs();
      refreshAvailableDrugs();
      showSuccess(`Đã thêm "${rowData.DrugName}" vào mẫu`);
    })
    .fail(err=> {
      const errorMsg = err.responseJSON?.error || err.statusText || 'Lỗi không xác định';
      if(err.status === 409) {
        showError('Thuốc này đã có trong mẫu rồi');
      } else {
        showError('Lỗi thêm thuốc: ' + errorMsg);
      }
    });
  });

  // Initialize
  $('#debug-info').text('Initializing...').show();
  
  Promise.all([loadTemplateInfo(), loadDrugGroups(), loadFormulations()])
    .then(() => {
      console.log('[DrugTemplateDetails] Initialization complete, loading template drugs');
      refreshTemplateDrugs();
    })
    .catch(err => {
      console.error('[DrugTemplateDetails] Initialization failed:', err);
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
  
  window.__drugTemplateDetailsDebug = { 
    reload: refreshTemplateDrugs, 
    templateData: ()=> dt?.data()?.toArray(),
    availableData: ()=> availableDt?.data()?.toArray()
  };
});
