// Signs CRUD & listing
$(document).ready(function(){
  const tableEl = $('#signs-table');
  let dt = null;
  let systemsCache = [];
  const modalEl = new bootstrap.Modal(document.getElementById('signModal'));

  function loadSystems(){
    return $.get('/api/body_system').then(resp => {
      const list = resp.body_system || [];
      systemsCache = list;
      const select = $('#filter-system');
      const formSelect = $('#SystemId');
      select.empty().append('<option value="">Hệ cơ quan (tất cả)</option>');
      formSelect.empty();
      list.forEach(sys => {
        select.append(`<option value="${sys.SystemId}">${sys.SystemName}</option>`);
        formSelect.append(`<option value="${sys.SystemId}">${sys.SystemName}</option>`);
      });
    });
  }

  function fetchData(){
    const params = {};
    const q = $('#search-desc').val().trim(); if(q) params.q = q;
    const t = $('#filter-type').val(); if(t !== '') params.type = t;
    const sys = $('#filter-system').val(); if(sys) params.system_id = sys;
    const spec = $('#filter-speciality').val().trim(); if(spec) params.speciality = spec;
    return $.get('/api/signs', params).then(resp => resp.signs || []);
  }

  function renderTable(rows){
    if(dt){ dt.destroy(); tableEl.empty(); }
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
      language:{
        search: 'Tìm:',
        lengthMenu: 'Hiển thị _MENU_',
        info: 'Hiển thị _START_ - _END_ / _TOTAL_',
        infoEmpty: '0 bản ghi',
        paginate: {previous:'Trước', next:'Tiếp'}
      }
    });
  }

  function refresh(){
    fetchData().then(renderTable).catch(err => alert('Lỗi tải dữ liệu: '+ (err.responseJSON?.error || err.statusText)));
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

  function debounce(fn, wait){ let t; return function(){ clearTimeout(t); t=setTimeout(fn, wait); }; }
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
  loadSystems().then(refresh);
});
