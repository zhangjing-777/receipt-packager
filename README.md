## ✅ Feature Overview

- Parse the provided JSON structure;
- Download each invoice file and place it into its corresponding category folder (e.g., `餐饮/悦来火锅店.pdf`);
- Package all folders into a single zip file (named `receipt_attachment_<timestamp>.zip`);
- Upload the zip file to Supabase Storage under the `lazy-receipt-summary/` bucket;
- Return the final downloadable link.
