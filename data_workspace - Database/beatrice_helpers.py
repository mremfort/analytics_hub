import pandas as pd
import datetime as dt
import streamlit as st
import plotly.graph_objects as go
import database as db

def load_metrics_data(file):
    with pd.ExcelFile(file) as xls:

        sheet_names = xls.sheet_names
        if 'New followers' in sheet_names:
            df = pd.read_excel(xls, sheet_name='New followers')
            df = df[["Date","Total followers"]]
            df.set_index(df.columns[0], inplace=True)
            df.index = pd.to_datetime(df.index)
        elif 'Visitor metrics' in sheet_names:
            df = pd.read_excel(xls, sheet_name='Visitor metrics')
            df = df[["Date", "Total unique visitors (total)", "Total page views (total)"]]
            df.set_index(df.columns[0], inplace=True)
            df.index = pd.to_datetime(df.index)
        elif 'Metrics' in sheet_names:
            df = pd.read_excel(xls, sheet_name='Metrics', header=1)
            df = df[["Date", "Unique impressions (organic)", "Clicks (total)", "Reactions (total)","Reposts (total)","Engagement rate (total)"]]
            df.set_index(df.columns[0], inplace=True)
            df.index = pd.to_datetime(df.index)
        else:
            st.error("None of the required sheets have been found")
            df = pd.DataFrame()
    return df

def load_post_data(content_file):
    with pd.ExcelFile(content_file) as xls:

        sheet_names = xls.sheet_names
        if 'All posts' in sheet_names:
            df = pd.read_excel(xls, sheet_name='All posts', header=1)
            df = df[["Post title","Post link","Created date","Impressions", "Clicks","Click through rate (CTR)","Likes","Comments", "Reposts", "Follows", "Engagement rate"]]
            df.set_index(df.columns[0], inplace=True)
        else:
            st.error("No posts found")
            df = pd.DataFrame()
    return df

def resample(df,period_type=None):
   """Filter dataframe based on time period (YTD, MTD, QTD)"""
   today = dt.date.today()
   if period_type == 'YTD':
       start_date = dt.date(today.year, 1, 1)
   elif period_type == 'MTD':
       start_date = dt.date(today.year, today.month, 1)
   elif period_type == 'QTD':
       start_date = dt.date(today.year, ((today.month - 1) // 3) * 3 + 1, 1)
   else:
       return df  # Return the original dataframe if no period specified
   return df[df.index.date >= start_date]


def calculate_totals(new_followers_df, unique_visitors_df, content_metrics_df, period=None):
   """Calculate total metrics for a given period"""
   # Filter data based on the specified period
   if period in ['YTD', 'MTD', 'QTD']:
       nf_df = resample(new_followers_df, period)
       uv_df = resample(unique_visitors_df, period)
       cm_df = resample(content_metrics_df, period)
   else:
       nf_df, uv_df, cm_df = new_followers_df, unique_visitors_df, content_metrics_df
   # Calculate totals
   total_new_followers = nf_df["Total followers"].sum()
   total_unique_visitors = uv_df["Total unique visitors (total)"].sum()
   total_impressions = cm_df["Unique impressions (organic)"].sum()
   total_clicks = cm_df["Clicks (total)"].sum()
   total_reposts = cm_df["Reposts (total)"].sum()
   return total_new_followers, total_unique_visitors, total_impressions, total_clicks, total_reposts

def calculate_average_engagement(content_metrics_df, period=None):
   """Calculate average engagement rate for a given period"""
   if period in ['YTD', 'MTD', 'QTD']:
       cm_df = resample(content_metrics_df, period)
   else:
       cm_df = content_metrics_df
   return cm_df["Engagement rate (total)"].mean()


def create_overview_chart(new_followers_df, unique_visitors_df, content_metrics_df,primary_color = "#10045a",secondary_color = "#025139", period=None):
    fig = go.Figure()

    # Resample data based on period (if provided)
    if period in ['YTD', 'MTD', 'QTD']:
        nf_df = resample(new_followers_df, period)
        uv_df = resample(unique_visitors_df, period)
        cm_df = resample(content_metrics_df, period)
    else:
        nf_df = new_followers_df
        uv_df = unique_visitors_df
        cm_df = content_metrics_df

    # Add the "New Followers" trace
    fig.add_trace(
        go.Scatter(x=nf_df.index.date, y=nf_df['Total followers'], mode='markers+lines', name="New Followers", line=dict(color=f"{primary_color}", width=2), marker=dict(symbol="circle", size=6)))

    # Add the "Unique Visitors" trace
    fig.add_trace(
        go.Scatter(x=uv_df.index.date, y=uv_df['Total unique visitors (total)'], mode='markers+lines', name="Unique Visitors", line=dict(color=f"{secondary_color}", width=2), marker=dict(symbol="circle", size=6)))
    #
    # # Add the "Content Metrics" trace
    fig.add_trace(
        go.Scatter(x=cm_df.index.date, y=cm_df['Unique impressions (organic)'], mode='markers+lines', name="Unique Impressions", line=dict(color="#025139", width=2), marker=dict(symbol="circle", size=6)))

    fig.add_trace(
        go.Scatter(x=cm_df.index.date, y=cm_df['Clicks (total)'], mode='markers+lines',
                   name="Total CLicks", line=dict(color="#510D6E", width=2), marker=dict(symbol="circle", size=6)))

    fig.add_trace(
        go.Scatter(x=cm_df.index.date, y=cm_df['Reposts (total)'], mode='markers+lines',
                   name="Reposts", line=dict(color="#63281F", width=2), marker=dict(symbol="circle", size=6)))

    # Update layout and trace styling
    fig.update_layout(
        title="Overview Chart",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Values",
        font=dict(
            family="Manrope, sans-serif",  # Body font
            size=14,
            color="black"
        ),
        title_font=dict(
            family="PT Serif, serif",  # Title font
            size=20,
            color="#10045A"  # Dark Blue for the title
        ),
        # plot_bgcolor="#F4F4F4",  # Light background color
        paper_bgcolor="white",  # Paper background color
        xaxis=dict(
            tickangle=45,
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        ),
        yaxis=dict(
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        )
    )

    fig.update_traces(hovertemplate='%{y}')

    return fig

def create_follower_chart(new_followers_df, custom=False, post_date = dt.date(2001, 1, 1),period=None, primary_color = "#10045a",secondary_color = "#025139"):
    fig = go.Figure()

    # Resample data based on period (if provided)
    if period in ['YTD', 'MTD', 'QTD']:
        nf_df = resample(new_followers_df, period)
    else:
        nf_df = new_followers_df

    # Add the "New Followers" trace
    fig.add_trace(
        go.Scatter(x=nf_df.index.date, y=nf_df['Total followers'], mode='markers+lines', name="New Followers", line=dict(color=f"{primary_color}", width=2), marker=dict(symbol="circle", size=6)))


    # Update layout and trace styling
    fig.update_layout(
        title=f"New Followers {period}",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Values",
        font=dict(
            family="Manrope, sans-serif",  # Body font
            size=14,
            color="black"
        ),
        title_font=dict(
            family="PT Serif, serif",  # Title font
            size=20,
            color="#10045A"  # Dark Blue for the title
        ),
        # plot_bgcolor="#F4F4F4",  # Light background color
        paper_bgcolor="white",  # Paper background color
        xaxis=dict(
            tickangle=45,
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        ),
        yaxis=dict(
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        )
    )

    fig.update_traces(hovertemplate='%{y}')

    return fig


def create_unique_visitors_chart(unique_visitors_df, period=None,primary_color = "#10045a",secondary_color = "#025139"):
    fig = go.Figure()

    # Resample data based on period (if provided)
    if period in ['YTD', 'MTD', 'QTD']:
        uv_df = resample(unique_visitors_df, period)
    else:
        uv_df = unique_visitors_df


    # Add the "Unique Visitors" trace
    fig.add_trace(
        go.Scatter(x=uv_df.index.date, y=uv_df['Total unique visitors (total)'], mode='markers+lines', name="Unique Visitors", line=dict(color=f"{primary_color}", width=2), marker=dict(symbol="circle", size=6)))


    # Update layout and trace styling
    fig.update_layout(
        title=f"Unique Visitors {period}",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Unique Followers",
        font=dict(
            family="Manrope, sans-serif",  # Body font
            size=14,
            color="black"
        ),
        title_font=dict(
            family="PT Serif, serif",  # Title font
            size=20,
            color="#10045A"  # Dark Blue for the title
        ),
        # plot_bgcolor="#F4F4F4",  # Light background color
        paper_bgcolor="white",  # Paper background color
        xaxis=dict(
            tickangle=45,
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        ),
        yaxis=dict(
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        )
    )

    fig.update_traces(hovertemplate='%{y}')

    return fig


def create_total_clicks_chart(content_metrics_df, period=None,primary_color = "#10045a",secondary_color = "#025139"):
    fig = go.Figure()

    # Resample data based on period (if provided)
    if period in ['YTD', 'MTD', 'QTD']:
        cm_df = resample(content_metrics_df, period)
    else:
        cm_df = content_metrics_df

    fig.add_trace(
        go.Scatter(x=cm_df.index.date, y=cm_df['Clicks (total)'], mode='markers+lines',
                   name="Total CLicks", line=dict(color=f"{primary_color}", width=2), marker=dict(symbol="circle", size=6)))

    # Update layout and trace styling
    fig.update_layout(
        title= f"Total Clicks {period}",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Total CLicks",
        font=dict(
            family="Manrope, sans-serif",  # Body font
            size=14,
            color="black"
        ),
        title_font=dict(
            family="PT Serif, serif",  # Title font
            size=20,
            color="#10045A"  # Dark Blue for the title
        ),
        # plot_bgcolor="#F4F4F4",  # Light background color
        paper_bgcolor="white",  # Paper background color
        xaxis=dict(
            tickangle=45,
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        ),
        yaxis=dict(
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        )
    )

    fig.update_traces(hovertemplate='%{y}')

    return fig




def create_total_impressions_chart(content_metrics_df, period=None,primary_color = "#10045a",secondary_color = "#025139"):
    fig = go.Figure()

    # Resample data based on period (if provided)
    if period in ['YTD', 'MTD', 'QTD']:
        cm_df = resample(content_metrics_df, period)
    else:
        cm_df = content_metrics_df

    #
    # # Add the "Content Metrics" trace
    fig.add_trace(
        go.Scatter(x=cm_df.index.date, y=cm_df['Unique impressions (organic)'], mode='markers+lines', name="Unique Impressions", line=dict(color=f"{primary_color}", width=2), marker=dict(symbol="circle", size=6)))


    # Update layout and trace styling
    fig.update_layout(
        title= f"Total Unique Impressions {period}",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Unique Impressions",
        font=dict(
            family="Manrope, sans-serif",  # Body font
            size=14,
            color="black"
        ),
        title_font=dict(
            family="PT Serif, serif",  # Title font
            size=20,
            color="#10045A"  # Dark Blue for the title
        ),
        # plot_bgcolor="#F4F4F4",  # Light background color
        paper_bgcolor="white",  # Paper background color
        xaxis=dict(
            tickangle=45,
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        ),
        yaxis=dict(
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        )
    )

    fig.update_traces(hovertemplate='%{y}')

    return fig


def create_reposts_chart(content_metrics_df, period=None,primary_color = "#10045a",secondary_color = "#025139"):
    fig = go.Figure()

    # Resample data based on period (if provided)
    if period in ['YTD', 'MTD', 'QTD']:
        cm_df = resample(content_metrics_df, period)
    else:
        cm_df = content_metrics_df

    fig.add_trace(
        go.Scatter(x=cm_df.index.date, y=cm_df['Reposts (total)'], mode='markers+lines',
                   name="Reposts", line=dict(color=f"{primary_color}", width=2), marker=dict(symbol="circle", size=6)))

    # Update layout and trace styling
    fig.update_layout(
        title= f"Reposts {period}",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Reposts",
        font=dict(
            family="Manrope, sans-serif",  # Body font
            size=14,
            color="black"
        ),
        title_font=dict(
            family="PT Serif, serif",  # Title font
            size=20,
            color="#10045A"  # Dark Blue for the title
        ),
        # plot_bgcolor="#F4F4F4",  # Light background color
        paper_bgcolor="white",  # Paper background color
        xaxis=dict(
            tickangle=45,
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        ),
        yaxis=dict(
            tickfont=dict(family="Manrope, sans-serif", size=12, color="darkgray"),
        )
    )

    fig.update_traces(hovertemplate='%{y}')

    return fig


def display_manual_entry_form(workspace):
    """
    Display a form that allows users to manually add or remove entries in database tables

    Parameters:
    workspace (str): The workspace name
    """
    tab1, tab2 = st.tabs(["Add Entry", "Remove Entry"])

    # Tab for adding entries
    with tab1:
        # Select the table to add data to
        table_name = st.selectbox(
            "Select Table",
            ["new_followers", "visitor_metrics", "content_metrics", "posts"],
            key=f"{workspace.lower().replace(' ', '_')}_table_select_add"
        )

        # Create form based on selected table
        if table_name == "new_followers":
            with st.form(key=f"{workspace.lower().replace(' ', '_')}_followers_form"):
                st.write("Add New Followers Entry")
                date = st.date_input("Date", key=f"{workspace.lower().replace(' ', '_')}_followers_date")
                total_followers = st.number_input("Total Followers", min_value=0, step=1,
                                                  key=f"{workspace.lower().replace(' ', '_')}_followers_count")

                submit_button = st.form_submit_button(label="Add Entry")
                if submit_button:
                    data = {
                        "date": date.strftime('%Y-%m-%d'),
                        "total_followers": total_followers
                    }
                    success = db.add_manual_entry(table_name, data, workspace)
                    if success:
                        st.success(f"Successfully added entry to {table_name}")
                    else:
                        st.error("Failed to add entry to database")

        elif table_name == "visitor_metrics":
            with st.form(key=f"{workspace.lower().replace(' ', '_')}_visitors_form"):
                st.write("Add Visitor Metrics Entry")
                date = st.date_input("Date", key=f"{workspace.lower().replace(' ', '_')}_visitors_date")
                unique_visitors = st.number_input("Total Unique Visitors", min_value=0, step=1,
                                                  key=f"{workspace.lower().replace(' ', '_')}_unique_visitors")
                page_views = st.number_input("Total Page Views", min_value=0, step=1,
                                             key=f"{workspace.lower().replace(' ', '_')}_page_views")

                submit_button = st.form_submit_button(label="Add Entry")
                if submit_button:
                    data = {
                        "date": date.strftime('%Y-%m-%d'),
                        "total_unique_visitors": unique_visitors,
                        "total_page_views": page_views
                    }
                    success = db.add_manual_entry(table_name, data, workspace)
                    if success:
                        st.success(f"Successfully added entry to {table_name}")
                    else:
                        st.error("Failed to add entry to database")

        elif table_name == "content_metrics":
            with st.form(key=f"{workspace.lower().replace(' ', '_')}_content_form"):
                st.write("Add Content Metrics Entry")
                date = st.date_input("Date", key=f"{workspace.lower().replace(' ', '_')}_content_date")
                impressions = st.number_input("Unique Impressions", min_value=0, step=1,
                                              key=f"{workspace.lower().replace(' ', '_')}_impressions")
                clicks = st.number_input("Clicks Total", min_value=0, step=1,
                                         key=f"{workspace.lower().replace(' ', '_')}_clicks")
                reactions = st.number_input("Reactions Total", min_value=0, step=1,
                                            key=f"{workspace.lower().replace(' ', '_')}_reactions")
                reposts = st.number_input("Reposts Total", min_value=0, step=1,
                                          key=f"{workspace.lower().replace(' ', '_')}_reposts")
                engagement = st.number_input("Engagement Rate", min_value=0.0, max_value=1.0,
                                             step=0.001, format="%.3f",
                                             key=f"{workspace.lower().replace(' ', '_')}_engagement")

                submit_button = st.form_submit_button(label="Add Entry")
                if submit_button:
                    data = {
                        "date": date.strftime('%Y-%m-%d'),
                        "unique_impressions": impressions,
                        "clicks_total": clicks,
                        "reactions_total": reactions,
                        "reposts_total": reposts,
                        "engagement_rate": engagement
                    }
                    success = db.add_manual_entry(table_name, data, workspace)
                    if success:
                        st.success(f"Successfully added entry to {table_name}")
                    else:
                        st.error("Failed to add entry to database")

        elif table_name == "posts":
            with st.form(key=f"{workspace.lower().replace(' ', '_')}_posts_form"):
                st.write("Add Post Entry")
                post_title = st.text_input("Post Title", key=f"{workspace.lower().replace(' ', '_')}_post_title")
                post_link = st.text_input("Post Link", key=f"{workspace.lower().replace(' ', '_')}_post_link")
                created_date = st.date_input("Created Date", key=f"{workspace.lower().replace(' ', '_')}_post_date")
                impressions = st.number_input("Impressions", min_value=0, step=1,
                                              key=f"{workspace.lower().replace(' ', '_')}_post_impressions")
                clicks = st.number_input("Clicks", min_value=0, step=1,
                                         key=f"{workspace.lower().replace(' ', '_')}_post_clicks")
                ctr = st.number_input("Click Through Rate", min_value=0.0, max_value=1.0,
                                      step=0.001, format="%.3f",
                                      key=f"{workspace.lower().replace(' ', '_')}_post_ctr")
                likes = st.number_input("Likes", min_value=0, step=1,
                                        key=f"{workspace.lower().replace(' ', '_')}_post_likes")
                comments = st.number_input("Comments", min_value=0, step=1,
                                           key=f"{workspace.lower().replace(' ', '_')}_post_comments")
                reposts = st.number_input("Reposts", min_value=0, step=1,
                                          key=f"{workspace.lower().replace(' ', '_')}_post_reposts")
                follows = st.number_input("Follows", min_value=0, step=1,
                                          key=f"{workspace.lower().replace(' ', '_')}_post_follows")
                engagement = st.number_input("Engagement Rate", min_value=0.0, max_value=1.0,
                                             step=0.001, format="%.3f",
                                             key=f"{workspace.lower().replace(' ', '_')}_post_engagement")

                submit_button = st.form_submit_button(label="Add Entry")
                if submit_button:
                    if not post_title:
                        st.error("Post Title is required")
                    else:
                        data = {
                            "post_title": post_title,
                            "post_link": post_link,
                            "created_date": created_date.strftime('%Y-%m-%d'),
                            "impressions": impressions,
                            "clicks": clicks,
                            "click_through_rate": ctr,
                            "likes": likes,
                            "comments": comments,
                            "reposts": reposts,
                            "follows": follows,
                            "engagement_rate": engagement
                        }
                        success = db.add_manual_entry(table_name, data, workspace)
                        if success:
                            st.success(f"Successfully added entry to {table_name}")
                        else:
                            st.error("Failed to add entry to database")

    # Tab for removing entries
    with tab2:
        # Select the table to remove data from
        removal_table = st.selectbox(
            "Select Table",
            ["new_followers", "visitor_metrics", "content_metrics", "posts"],
            key=f"{workspace.lower().replace(' ', '_')}_table_select_remove"
        )

        removal_method = st.radio(
            "Removal Method",
            ["Delete Single Entry", "Delete Date Range"],
            key=f"{workspace.lower().replace(' ', '_')}_removal_method"
        )

        if removal_method == "Delete Single Entry":
            # Get entries to show in the selection dropdown
            entries = db.get_entries(removal_table, workspace)

            if entries:
                # Format entries for display based on table type
                if removal_table == "new_followers":
                    entry_options = [f"ID: {entry[0]} - Date: {entry[1]} - Followers: {entry[2]}" for entry in entries]
                elif removal_table == "visitor_metrics":
                    entry_options = [f"ID: {entry[0]} - Date: {entry[1]} - Visitors: {entry[2]}" for entry in entries]
                elif removal_table == "content_metrics":
                    entry_options = [f"ID: {entry[0]} - Date: {entry[1]} - Impressions: {entry[2]}" for entry in
                                     entries]
                elif removal_table == "posts":
                    entry_options = [f"ID: {entry[0]} - Title: {entry[1]} - Date: {entry[2]}" for entry in entries]

                selected_entry = st.selectbox(
                    "Select Entry to Delete",
                    options=entry_options,
                    key=f"{workspace.lower().replace(' ', '_')}_entry_select"
                )

                # Extract the ID from the selected entry
                entry_id = int(selected_entry.split(" - ")[0].replace("ID: ", ""))

                if st.button("Delete Selected Entry", key=f"{workspace.lower().replace(' ', '_')}_delete_single"):
                    # Confirm deletion
                    confirm = st.warning("Are you sure you want to delete this entry? This action cannot be undone.")
                    confirm_col1, confirm_col2 = st.columns(2)
                    with confirm_col1:
                        if st.button("Yes, Delete", key=f"{workspace.lower().replace(' ', '_')}_confirm_delete"):
                            success = db.delete_entry(removal_table, entry_id)
                            if success:
                                st.success(f"Entry deleted successfully!")
                                # Force refresh by rerunning the app
                                st.experimental_rerun()
                            else:
                                st.error("Failed to delete entry from database")
                    with confirm_col2:
                        if st.button("Cancel", key=f"{workspace.lower().replace(' ', '_')}_cancel_delete"):
                            st.experimental_rerun()
            else:
                st.warning(f"No entries found in {removal_table} for {workspace}")

        elif removal_method == "Delete Date Range":
            # Date range selection
            start_date = st.date_input(
                "Start Date",
                key=f"{workspace.lower().replace(' ', '_')}_range_start"
            )
            end_date = st.date_input(
                "End Date",
                key=f"{workspace.lower().replace(' ', '_')}_range_end"
            )

            if st.button("Delete Date Range", key=f"{workspace.lower().replace(' ', '_')}_delete_range"):
                # Confirm deletion
                confirm = st.warning(
                    f"Are you sure you want to delete all entries between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}? This action cannot be undone.")
                confirm_col1, confirm_col2 = st.columns(2)
                with confirm_col1:
                    if st.button("Yes, Delete Range", key=f"{workspace.lower().replace(' ', '_')}_confirm_range"):
                        deleted_count = db.delete_entries_by_date_range(
                            removal_table,
                            workspace,
                            start_date.strftime('%Y-%m-%d'),
                            end_date.strftime('%Y-%m-%d')
                        )
                        if deleted_count > 0:
                            st.success(f"Successfully deleted {deleted_count} entries from {removal_table}")
                            # Force refresh by rerunning the app
                            st.experimental_rerun()
                        else:
                            st.info(f"No entries found in the specified date range")
                with confirm_col2:
                    if st.button("Cancel Range Delete", key=f"{workspace.lower().replace(' ', '_')}_cancel_range"):
                        st.experimental_rerun()