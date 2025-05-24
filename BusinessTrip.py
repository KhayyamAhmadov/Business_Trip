# Previous code for admin_tabs[0] (Dashboard) and other tabs...
# The error is in the following block, which is an intermediate version of admin_tabs[1].

# This is the problematic admin_tabs[1] block that needs correction.
# It appears in the middle of the user's script.
# The comment "# 2. MƏLUMAT İDARƏETMƏSİ TAB hissəsindəki kodu aşağıdakı kimi düzəldin:"
# refers to THIS block.

with admin_tabs[1]: # Məlumat İdarəetməsi (Data Management)
    st.markdown("### 🗂️ Məlumatların İdarə Edilməsi")
    
    try:
        df = load_trip_data()
        
        if not df.empty:
            # Tarix sütunlarını avtomatik çevir
            date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Filtr və axtarış seçimləri
            st.markdown("#### 🔍 Filtr və Axtarış")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_filter_options = ["Hamısı", "Son 7 gün", "Son 30 gün", "Son 3 ay", "Bu il", "Seçilmiş aralıq"]
                # Ensure date_filter is initialized, e.g. to "Hamısı" if not "Seçilmiş aralıq"
                date_filter = st.selectbox(
                    "📅 Tarix filtri",
                    date_filter_options,
                    index=0 # Default to "Hamısı"
                )
                
                # Initialize start_date and end_date to avoid NameError if "Seçilmiş aralıq" is not chosen first
                start_date_filter = None
                end_date_filter = None
                if date_filter == "Seçilmiş aralıq":
                    start_date_filter = st.date_input("Başlanğıc tarixi (filtr)") # Renamed to avoid conflict
                    end_date_filter = st.date_input("Bitmə tarixi (filtr)")   # Renamed to avoid conflict
            
            with col2:
                selected_dept = "Hamısı" # Default value
                if 'Şöbə' in df.columns:
                    departments = ["Hamısı"] + sorted(df['Şöbə'].unique().tolist())
                    selected_dept = st.selectbox("🏢 Şöbə filtri", departments)
            
            with col3:
                selected_type = "Hamısı" # Default value
                if 'Ezamiyyət növü' in df.columns:
                    trip_types = ["Hamısı"] + df['Ezamiyyət növü'].unique().tolist()
                    selected_type = st.selectbox("✈️ Ezamiyyət növü", trip_types)
            
            search_term = st.text_input("🔎 Ad və ya soyad üzrə axtarış")

            # Filtirləmə məntiqi
            filtered_df = df.copy()
            if date_filter != "Hamısı" and 'Tarix' in df.columns:
                if date_filter == "Seçilmiş aralıq":
                    if start_date_filter and end_date_filter: # Check if dates are set
                        filtered_df = filtered_df[
                            (filtered_df['Tarix'].dt.date >= start_date_filter) & 
                            (filtered_df['Tarix'].dt.date <= end_date_filter)
                        ]
                else:
                    now = datetime.now()
                    cutoff = None
                    if date_filter == "Son 7 gün":
                        cutoff = now - timedelta(days=7)
                    elif date_filter == "Son 30 gün":
                        cutoff = now - timedelta(days=30)
                    elif date_filter == "Son 3 ay":
                        cutoff = now - timedelta(days=90)
                    elif date_filter == "Bu il":
                        cutoff = datetime(now.year, 1, 1)
                    if cutoff:
                        filtered_df = filtered_df[filtered_df['Tarix'] >= cutoff]

            if selected_dept != "Hamısı" and 'Şöbə' in df.columns:
                filtered_df = filtered_df[filtered_df['Şöbə'] == selected_dept]

            if selected_type != "Hamısı" and 'Ezamiyyət növü' in df.columns:
                filtered_df = filtered_df[filtered_df['Ezamiyyət növü'] == selected_type]

            if search_term and 'Ad' in filtered_df.columns and 'Soyad' in filtered_df.columns: # Ensure columns exist
                mask = filtered_df['Ad'].astype(str).str.contains(search_term, case=False, na=False) | \
                       filtered_df['Soyad'].astype(str).str.contains(search_term, case=False, na=False)
                filtered_df = filtered_df[mask]
            
            # Corrected block for displaying data_editor
            st.markdown(f"#### 📊 Nəticələr ({len(filtered_df)} qeyd)") # Added for clarity

            if not filtered_df.empty:
                # Sütun konfiqurasiyası (Moved definition here)
                column_config = {}
                for col_name in filtered_df.columns: # Use a different variable name for the loop
                    if col_name in date_columns:
                        column_config[col_name] = st.column_config.DatetimeColumn(
                            col_name,
                            format="DD.MM.YYYY HH:mm" if col_name == 'Tarix' else "DD.MM.YYYY"
                        )
                    elif col_name in ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti']:
                        column_config[col_name] = st.column_config.NumberColumn(
                            col_name,
                            format="%.2f AZN"
                        )
                
                # Correctly indented and using filtered_df
                edited_df = st.data_editor(
                    filtered_df, # Changed from display_df to filtered_df
                    column_config=column_config, # Now defined
                    use_container_width=True,
                    height=600,
                    key="admin_data_editor_intermediate" # Changed key to avoid conflict if other editors exist
                )
                
                # Dəyişiklikləri saxla
                if st.button("💾 Dəyişiklikləri Saxla", type="primary", key="save_changes_intermediate_btn"):
                    try:
                        # Tarix sütunlarını formatla
                        for col_name_save in date_columns: # Use a different variable name
                            if col_name_save in edited_df.columns:
                                edited_df[col_name_save] = pd.to_datetime(edited_df[col_name_save], errors='coerce')
                        
                        # Find original indices in df to update
                        # This is a complex part: st.data_editor might return a df with reset index
                        # For simplicity, assuming edited_df can be used to update a full save,
                        # or a more robust merge/update strategy is needed if only partial df is edited.
                        # The user's final version implies updating the main 'df' then saving 'df'.
                        # We need to map `edited_df` rows back to `df` rows if `filtered_df` was a subset.
                        # A simpler approach if `filtered_df` is what we want to save after editing:
                        
                        # If `df` is the source of truth and `filtered_df` is a view, updating is tricky.
                        # For now, let's assume the user wants to save the *entire* df after updates from `edited_df`
                        # This requires merging `edited_df` back into `df` based on original indices.
                        # The simplest interpretation from the given code is that `df.update(edited_df)`
                        # works if `edited_df` has the same index as `df`.
                        # `st.data_editor` preserves the index of the input DataFrame.
                        
                        # Update the original DataFrame `df` with changes from `edited_df`
                        # This assumes `edited_df` contains rows that are also in `df` and share the same index.
                        # If `filtered_df` was a true subset, `df.update` will update only matching indexed rows.
                        
                        # To correctly update, we use the index of filtered_df to update the main df
                        for idx in edited_df.index:
                            if idx in df.index: # Ensure index exists in original df
                                df.loc[idx] = edited_df.loc[idx]
                        
                        # Faylı saxla (the original 'df' which has now been updated)
                        df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                        st.success("✅ Dəyişikliklər saxlanıldı!")
                        write_log("Data Edited", f"{len(edited_df[edited_df.apply(lambda x: x.equals(filtered_df.loc[x.name]), axis=1)==False])} rows changed.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Saxlama xətası: {str(e)}")
            
            else: # Corresponds to `if not filtered_df.empty:`
                st.info("🔍 Filtrə uyğun qeyd tapılmadı")
            
            # The `else: st.warning("Zəhmət olmasa göstəriləcək sütunları seçin")` was removed
            # as its corresponding `if` condition was unclear and not directly tied to the data_editor.
        
        else: # Corresponds to `if not df.empty:`
            st.warning("📭 Hələ heç bir məlumat yoxdur")
            
    except Exception as e:
        st.error(f"❌ Məlumat idarəetməsi xətası: {str(e)}")
