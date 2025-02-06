# hathi-pd-2025



1. Download collection
2. python3 compress_hathi_collection_source.py
3. gzip -9 ../data/hathi_collection.ndjson
4. python3 download_hathi_marc.py
5. python3 compress_hathi_marc_into_collection.py
6. python3 download_oclc.py
7. python3 compress_oclc_data_into_collection.py
8. python3 download_holdings.py
9. python3 compress_holdings_data_into_collection.py
10. python3 download_hathi_web_meta.py
11. python3 download_lccns.py
12. python3 download_lcsh.py
13. python3 download_lcsh.py
14. python3 download_name_titles.py
15. python3 download_covers.py
16. python3 check_against_gutenberg.py
17. python3 process_final_data.py
18. python3 build_hiearchy.py
19. python3 build_hiearchy_counts.py
20. python3 build_browser_data.py
21. python3 build_pagefind_html.py
22. npx -y pagefind --site "output_dir_of_build_pagefind_html"
