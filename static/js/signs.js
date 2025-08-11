// Signs CRUD & listing
$(document).ready(function(){
  console.log('[Signs] Document ready');
  const tableEl = $('#signs-table');
  if(!tableEl.length){ console.error('[Signs] Table element #signs-table not found'); return; }
  if(!$.fn.DataTable){ console.error('[Signs] DataTables plugin not loaded'); }
  let dt = null;
  let systemsCache = [];
  const modalEl = new bootstrap.Modal(document.getElementById('signModal'));

  function loadSystems(){
    console.log('[Signs] Loading body systems...');
    return $.get('/api/body_system')
      .then(resp => {
        const list = resp.body_system || [];
        console.log('[Signs] Body systems fetched:', list.length);
        if(!Array.isArray(list) || list.length === 0){
          console.warn('[Signs] No body systems returned; attempting fallback via /api/signs');
          return fallbackSystemsFromSigns();
        }
        populateSystems(list);
        return list;
      })
      .catch(err => {
        console.error('[Signs] Error loading body systems:', err);
        showError('Không tải được danh sách hệ cơ quan');
        return fallbackSystemsFromSigns();
      });
  }

  function populateSystems(list){
    systemsCache = list;
    const select = $('#filter-system');
    const formSelect = $('#SystemId');
    select.empty().append('<option value="">Hệ cơ quan (tất cả)</option>');
    formSelect.empty();
    list.forEach(sys => {
      if(sys && sys.SystemId !== undefined){
        select.append(`<option value="${sys.SystemId}">${sys.SystemName || ('Hệ '+sys.SystemId)}</option>`);
        formSelect.append(`<option value="${sys.SystemId}">${sys.SystemName || ('Hệ '+sys.SystemId)}</option>`);
      }
    });
    if(list.length === 0){
      select.append('<option disabled>(Không có dữ liệu hệ)</option>');
    }
  }

  function fallbackSystemsFromSigns(){
    return $.get('/api/signs')
      .then(resp => {
        const signs = resp.signs || [];
        const map = new Map();
        signs.forEach(s => { if(s.SystemId && !map.has(s.SystemId)) map.set(s.SystemId, s.SystemName); });
        const fallbackList = Array.from(map.entries()).map(([SystemId, SystemName]) => ({SystemId, SystemName}));
        console.log('[Signs] Fallback systems derived from signs:', fallbackList.length);
        populateSystems(fallbackList);
        if(fallbackList.length === 0){
          showInfo('Không tìm thấy Hệ cơ quan để lọc');
        }
        return fallbackList;
      })
      .catch(err => {
        console.error('[Signs] Fallback derivation failed:', err);
        return [];
      });
  }

  function fetchData(){
    const params = {};
    const q = $('#search-desc').val().trim(); if(q) params.q = q;
    const t = $('#filter-type').val(); if(t !== '') params.type = t;
    const sys = $('#filter-system').val(); if(sys) params.system_id = sys;
    const spec = $('#filter-speciality').val().trim(); if(spec) params.speciality = spec;
    console.log('Fetching /api/signs with params', params);
    return $.get('/api/signs', params)
      .then(resp => {
        let rows = resp.signs || [];
        if(rows.length === 0) {
          console.log('Primary endpoint returned 0 rows, trying fallback /api/sign');
          return $.get('/api/sign').then(r2 => (r2.sign || r2.signs || [])).catch(()=>rows);
        }
        return rows;
      })
      .catch(err => {
        console.error('Error fetching /api/signs', err);
        showError('Không tải được dữ liệu từ /api/signs');
        return [];
      });
  }

  function renderTable(rows){
  console.log('[Signs] Rendering table with rows:', rows.length);
  if(dt){ dt.destroy(); tableEl.find('tbody').empty(); }
  dt = tableEl.DataTable({
      data: rows,
      columns: [
    {data:'SignId', title:'ID', visible:false},
        {data:'SignDesc', title:'Mô tả'},
        {data:'SignType', title:'Loại', render:(d)=> d?'<span class="badge bg-danger">Thực thể</span>':'<span class="badge bg-info text-dark">Cơ năng</span>'},
        {data:'SystemName', title:'Hệ'},
        {data:'Speciality', title:'Chuyên khoa', defaultContent:''},
        {data:null, title:'', orderable:false, width:'90px', render:(row)=> `\n          <div class='btn-group btn-group-sm'>\n            <button class='btn btn-outline-success btn-edit' title='Sửa'><i class='fas fa-edit'></i></button>\n            <button class='btn btn-outline-danger btn-del' title='Xóa'><i class='fas fa-trash'></i></button>\n          </div>`}
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
        paginate: {previous:'Trước', next:'Tiếp'}
      }
    });
    console.log('[Signs] DataTable initialized');
  $('#signs-debug').text('Loaded rows: '+rows.length).show();
    setTimeout(()=>{
      const displayed = tableEl.find('tbody tr').length;
      if(rows.length && !displayed){
        console.warn('[Signs] Fallback manual render triggered');
        const tbody = tableEl.find('tbody');
        tbody.empty();
        rows.forEach(r=>{
          tbody.append(`<tr data-id='${r.SignId}'>
            <td style='display:none'>${r.SignId}</td>
            <td>${escapeHtml(r.SignDesc||'')}</td>
            <td>${r.SignType?'<span class=\"badge bg-danger\">Thực thể</span>':'<span class=\"badge bg-info text-dark\">Cơ năng</span>'}</td>
            <td>${escapeHtml(r.SystemName||'')}</td>
            <td>${escapeHtml(r.Speciality||'')}</td>
            <td><div class='btn-group btn-group-sm'>
              <button class='btn btn-outline-success btn-edit' title='Sửa'><i class='fas fa-edit'></i></button>
              <button class='btn btn-outline-danger btn-del' title='Xóa'><i class='fas fa-trash'></i></button>
            </div></td>
          </tr>`);
        });
      }
    }, 200);
  }

  function refresh(){
    $('#alert-container').empty();
  $('#signs-debug').text('Fetching data...').show();
    fetchData().then(rows => {
      renderTable(rows);
      if(rows.length === 0){
        showInfo('Không có dấu hiệu phù hợp bộ lọc.');
      }
    }).catch(err => showError('Lỗi tải dữ liệu: '+ (err?.responseJSON?.error || err?.statusText || err)));
  }

  function clearForm(){
    $('#SignId').val('');
    $('#SignDesc').val('');
    $('#SignType').val('0');
    $('#SystemId').val(systemsCache[0]? systemsCache[0].SystemId : '');
    $('#Speciality').val('');
  }

  $('#btn-add-sign').on('click', function(){
    clearForm();
    $('#modalTitle').text('Thêm dấu hiệu');
    modalEl.show();
  });

  function debounce(fn, wait){ let t; return function(){ const ctx=this, args=arguments; clearTimeout(t); t=setTimeout(()=>fn.apply(ctx,args), wait); }; }
  $('#btn-refresh, #filter-type, #filter-system').on('click change', refresh);
  $('#search-desc, #filter-speciality').on('keyup', debounce(refresh, 400));

  // Save
  $('#btn-save-sign').on('click', function(){
    const payload = {
      SignDesc: $('#SignDesc').val().trim(),
      SignType: $('#SignType').val(),
      SystemId: $('#SystemId').val(),
      Speciality: $('#Speciality').val().trim()
    };
    if(!payload.SignDesc){ alert('Mô tả bắt buộc'); return; }
    if(!payload.SystemId){ alert('Chọn hệ cơ quan'); return; }
    const id = $('#SignId').val();
    const method = id? 'PUT':'POST';
    const url = id? `/api/signs/${id}`:'/api/signs';
    $.ajax({url, method, contentType:'application/json', data: JSON.stringify(payload)})
      .done(()=>{ modalEl.hide(); refresh(); })
      .fail(err=> alert('Lỗi lưu: ' + (err.responseJSON?.error || err.statusText)));
  });

  // Row actions
  tableEl.on('click', '.btn-edit', function(){
    const data = dt.row($(this).closest('tr')).data();
    if(!data) return;
    $('#SignId').val(data.SignId);
    $('#SignDesc').val(data.SignDesc);
    $('#SignType').val(data.SignType);
    $('#SystemId').val(data.SystemId);
    $('#Speciality').val(data.Speciality || '');
    $('#modalTitle').text('Cập nhật dấu hiệu');
    modalEl.show();
  });

  tableEl.on('click', '.btn-del', function(){
    const data = dt.row($(this).closest('tr')).data();
    if(!data) return;
    if(!confirm('Xóa dấu hiệu này?')) return;
    $.ajax({url:`/api/signs/${data.SignId}`, method:'DELETE'})
      .done(()=> refresh())
      .fail(err=> alert('Lỗi xóa: ' + (err.responseJSON?.error || err.statusText)));
  });

  // Initialize
  $('#signs-debug').text('Initializing...').show();
  loadSystems().then(refresh);
  $(window).on('load', ()=> console.log('[Signs] Window load complete'));

  function showAlert(html, type){
    const id = 'alert-'+Date.now();
    $('#alert-container').append(`<div id='${id}' class='alert alert-${type} py-1 my-2'>${html}</div>`);
    setTimeout(()=> $('#'+id).fadeOut(400, function(){ $(this).remove(); }), 4000);
  }
  function showError(msg){ showAlert(`<i class='fas fa-exclamation-triangle me-1'></i>${msg}`,'danger'); }
  function showInfo(msg){ showAlert(`<i class='fas fa-info-circle me-1'></i>${msg}`,'info'); }
  function escapeHtml(str){ return String(str).replace(/[&<>"']/g, s=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[s])); }
  window.__signsDebug = { reload: refresh };
});
