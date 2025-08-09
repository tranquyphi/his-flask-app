#!/bin/bash
# Script to fix pandas import and rollback issues in excel functions

echo "Fixing excel_functions2.py..."

# Fix imports for all functions in excel_functions2.py
sed -i '2s/from models import/import pandas as pd\n    from models import/' /root/his/api/excel_functions2.py
sed -i '111s/from models import/import pandas as pd\n    from models import/' /root/his/api/excel_functions2.py
sed -i '232s/from models import/import pandas as pd\n    from models import/' /root/his/api/excel_functions2.py

# Fix exception handling in excel_functions2.py
sed -i 's/        except Exception as e:/        except Exception as e:\n            db.session.rollback()  # Reset session state after constraint violation/' /root/his/api/excel_functions2.py

echo "Fixing excel_functions3.py..."

# Fix imports for all functions in excel_functions3.py  
sed -i '2s/from models import/import pandas as pd\n    from models import/' /root/his/api/excel_functions3.py

# Fix exception handling in excel_functions3.py
sed -i 's/        except Exception as e:/        except Exception as e:\n            db.session.rollback()  # Reset session state after constraint violation/' /root/his/api/excel_functions3.py

echo "Done!"
