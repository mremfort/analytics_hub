import streamlit as st
from beatrice_helpers import load_metrics_data, load_post_data, calculate_totals, calculate_average_engagement
from beatrice_helpers import create_overview_chart, create_follower_chart, create_unique_visitors_chart
from beatrice_helpers import create_total_clicks_chart, create_total_impressions_chart, create_reposts_chart
import webbrowser
import pandas as pd
import database as db


# Set page configuration
def display_christina():
    workspace = "Christina Lewis"

    # Initialize database if it doesn't exist
    if not db.db_exists():
        db.init_db()

    with st.sidebar:
        with st.popover(label="Upload Data", use_container_width=True):
            followers_file = st.file_uploader("Upload LinkedIn Followers File", type=["xls", "xlsx"],
                                              key="cl_followers")
            visitors_file = st.file_uploader("Upload LinkedIn Visitors File", type=["xls", "xlsx"], key="cl_visitors")
            content_file = st.file_uploader("Upload LinkedIn Content File", type=["xls", "xlsx"], key="cl_content")

            if st.button("Save Data to Database", key="cl_save_data"):
                if followers_file and visitors_file and content_file:
                    # Load data from files
                    new_followers_df = load_metrics_data(followers_file)
                    visitor_metrics_df = load_metrics_data(visitors_file)
                    content_metrics_df = load_metrics_data(content_file)
                    post_df = load_post_data(content_file)

                    # Save data to database
                    db.save_followers_data(new_followers_df, workspace)
                    db.save_visitor_metrics(visitor_metrics_df, workspace)
                    db.save_content_metrics(content_metrics_df, workspace)
                    db.save_posts_data(post_df, workspace)

                    st.success("Data saved to database successfully!")
                else:
                    st.error("Please upload all three files to save to database")

        with st.popover(label="Styles", use_container_width=True):
            primary_color = st.color_picker("Primary Color", "#510D6E", key="cl_primary")
            secondary_color = st.color_picker("Secondary Color", "#63281F", key="cl_Secondary")

    st.title("Christina Lewis")
    tabs = st.tabs(["Account Metrics", "Post Metrics"])

    # First check if data exists in the database
    has_data = db.has_workspace_data(workspace)

    # If we have uploaded files, use those
    if followers_file and visitors_file and content_file:
        new_followers_df = load_metrics_data(followers_file)
        visitor_metrics_df = load_metrics_data(visitors_file)
        content_metrics_df = load_metrics_data(content_file)
        post_df = load_post_data(content_file)
        data_source = "files"
    # Otherwise, if we have data in the database, use that
    elif has_data:
        new_followers_df = db.load_followers_data(workspace)
        visitor_metrics_df = db.load_visitor_metrics(workspace)
        content_metrics_df = db.load_content_metrics(workspace)
        post_df = db.load_posts_data(workspace)
        data_source = "database"
        st.info("Using data from database. Upload new files to update.")
    # If no data is available, show error
    else:
        st.error("Please upload all three files or initialize the database first")
        return

    # Display account metrics
    with tabs[0]:
        st.subheader("Growth Overview")
        time_horizon = st.radio(label="Time Horizon", options=["LTD", "YTD", "MTD", "QTD"], horizontal=True,
                                key="cl_time_horizon")
        total_new_followers, total_unique_visitors, total_impressions, total_clicks, total_reposts = calculate_totals(
            new_followers_df, visitor_metrics_df, content_metrics_df, time_horizon)
        average_engagement = calculate_average_engagement(content_metrics_df, time_horizon)

        nf_col, uv_col, ti_col = st.columns(3)
        tc_col, tr_col, ae_col = st.columns(3)

        with nf_col:
            st.metric(label="Total New Followers", value=f"{total_new_followers:,}", border=True)
        with uv_col:
            st.metric(label="Total Unique Visitors", value=f"{total_unique_visitors:,}", border=True)
        with ti_col:
            st.metric(label="Total Impressions", value=f"{total_impressions:,}", border=True)
        with tc_col:
            st.metric(label="Total Clicks", value=f"{total_clicks:,}", border=True)
        with tr_col:
            st.metric(label="Total Reposts", value=f"{total_reposts:,}", border=True)
        with ae_col:
            st.metric(label="Average Engagement", value=f"{round(average_engagement * 100, 2)}%", border=True)

        overview_chart = create_overview_chart(new_followers_df, visitor_metrics_df, content_metrics_df,
                                               primary_color=primary_color, secondary_color=secondary_color,
                                               period=time_horizon)
        follower_chart = create_follower_chart(new_followers_df, period=time_horizon, primary_color=primary_color,
                                               secondary_color=secondary_color)
        unique_visitors_chart = create_unique_visitors_chart(visitor_metrics_df, period=time_horizon,
                                                             primary_color=primary_color,
                                                             secondary_color=secondary_color)
        total_clicks_chart = create_total_clicks_chart(content_metrics_df, period=time_horizon,
                                                       primary_color=primary_color, secondary_color=secondary_color)
        total_impressions_chart = create_total_impressions_chart(content_metrics_df, period=time_horizon,
                                                                 primary_color=primary_color,
                                                                 secondary_color=secondary_color)
        reposts_chart = create_reposts_chart(content_metrics_df, period=time_horizon, primary_color=primary_color,
                                             secondary_color=secondary_color)

        nf_chart_col, uv_chart_col = st.columns(2)
        tc_chart_col, ti_chart_col = st.columns(2)
        tr_chart_col, temp_col = st.columns(2)

        with nf_chart_col:
            st.write(follower_chart)
        with uv_chart_col:
            st.write(unique_visitors_chart)
        with tc_chart_col:
            st.write(total_clicks_chart)
        with ti_chart_col:
            st.write(total_impressions_chart)
        with tr_chart_col:
            st.write(reposts_chart)
        st.write(overview_chart)

    # Display post metrics
    with tabs[1]:
        if not post_df.empty:
            post_title = st.selectbox("Select a Post", post_df.index, key="cl_post_select")
            selected_post = post_df[post_df.index == post_title].iloc[0]

            # Display the metrics for the selected post
            cd_col, pi_col, pc_col = st.columns(3)
            with cd_col:
                st.metric(label="Created date", value=f"{selected_post['Created date']}", border=True)
            with pi_col:
                st.metric(label="Impressions", value=f"{selected_post['Impressions']:,}", border=True)
            with pc_col:
                st.metric(label="Clicks", value=f"{selected_post['Clicks']:,}", border=True)

            ctr_col, pl_col, pr_col = st.columns(3)
            with ctr_col:
                st.metric(label="Click through rate (CTR)", value=f"{selected_post['Click through rate (CTR)']:.2%}",
                          border=True)
            with pl_col:
                st.metric(label="Likes", value=f"{selected_post['Likes']:,}", border=True)
            with pr_col:
                st.metric(label="Reposts", value=f"{selected_post['Reposts']:,}", border=True)

            pf_col, pe_col, blank_col = st.columns(3)
            with pf_col:
                st.metric(label="Follows", value=f"{selected_post['Follows']:,}", border=True)
            with pe_col:
                st.metric(label="Engagement rate", value=f"{selected_post['Engagement rate']:.2%}", border=True)

            if st.button("View Post", key="cl_view_post"):
                webbrowser.open(f"{selected_post['Post link']}")
        else:
            st.error("No posts data available")