# 🔎 FDA Device API Test URLs (Query: Medtronic)

Each URL below retrieves the **50 most recent** records (where possible) from different FDA device datasets.

---

## Category: device

**510k (device_name)**  
https://api.fda.gov/device/510k.json?search=device_name:Medtronic&limit=50&sort=decision_date:desc

**event (device.brand_name)**  
https://api.fda.gov/device/event.json?search=device.brand_name:Medtronic&limit=50&sort=date_received:desc

**event (device.generic_name)**  
https://api.fda.gov/device/event.json?search=device.generic_name:Medtronic&limit=50&sort=date_received:desc

**recall (product_description)**  
https://api.fda.gov/device/recall.json?search=product_description:Medtronic&limit=50

**classification (device_name)**  
https://api.fda.gov/device/classification.json?search=device_name:Medtronic&limit=50

**pma (trade_name)**  
https://api.fda.gov/device/pma.json?search=trade_name:Medtronic&limit=50&sort=decision_date:desc

**udi (brand_name)**  
https://api.fda.gov/device/udi.json?search=brand_name:Medtronic&limit=50

**udi (device_description)**  
https://api.fda.gov/device/udi.json?search=device_description:Medtronic&limit=50

---

## Category: manufacturer

**510k (applicant)**  
https://api.fda.gov/device/510k.json?search=applicant:Medtronic&limit=50&sort=decision_date:desc

**event (manufacturer_d_name)**  
https://api.fda.gov/device/event.json?search=manufacturer_d_name:Medtronic&limit=50&sort=date_received:desc

**event (manufacturer_name)**  
https://api.fda.gov/device/event.json?search=manufacturer_name:Medtronic&limit=50&sort=date_received:desc

**recall (recalling_firm)**  
https://api.fda.gov/device/recall.json?search=recalling_firm:Medtronic&limit=50

**recall (manufacturer_name)**  
https://api.fda.gov/device/recall.json?search=manufacturer_name:Medtronic&limit=50

**pma (applicant)**  
https://api.fda.gov/device/pma.json?search=applicant:Medtronic&limit=50&sort=decision_date:desc

**udi (company_name)**  
https://api.fda.gov/device/udi.json?search=company_name:Medtronic&limit=50

---

## Category: k_number (example: K123456)

**510k**  
https://api.fda.gov/device/510k.json?search=k_number:K123456&limit=50&sort=decision_date:desc

**recall**  
https://api.fda.gov/device/recall.json?search=k_numbers:K123456&limit=50

---

## Category: pma_number (example: P010001)

**pma**  
https://api.fda.gov/device/pma.json?search=pma_number:P010001&limit=50&sort=decision_date:desc

**recall**  
https://api.fda.gov/device/recall.json?search=pma_numbers:P010001&limit=50

---

## Category: product_code (example: MNT)

**510k**  
https://api.fda.gov/device/510k.json?search=product_code:MNT&limit=50&sort=decision_date:desc

**event**  
https://api.fda.gov/device/event.json?search=device.device_report_product_code:MNT&limit=50&sort=date_received:desc

**recall**  
https://api.fda.gov/device/recall.json?search=product_code:MNT&limit=50

**classification**  
https://api.fda.gov/device/classification.json?search=product_code:MNT&limit=50

**pma**  
https://api.fda.gov/device/pma.json?search=product_code:MNT&limit=50&sort=decision_date:desc

**udi**  
https://api.fda.gov/device/udi.json?search=product_codes:MNT&limit=50

---

## Category: udi_di (example: 12345678901234)

**udi**  
https://api.fda.gov/device/udi.json?search=device_id:12345678901234&limit=50