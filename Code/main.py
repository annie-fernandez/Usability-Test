import streamlit as st
import csv
import os
import time
import pandas as pd
import altair as alt

if "completed" not in st.session_state:
    st.session_state.completed = False
if "page" not in st.session_state:
    st.session_state.page = 0

with st.sidebar:
    st.caption("Navigation")
    if st.button("View Report", use_container_width=True):
        st.session_state.page = 5
        st.rerun()

pages = ["Home", "Consent", "Demographics", "Tasks", "Exit Questionnaire", "Report"]

with st.container(border=True):
    st.progress(st.session_state.page / (len(pages) - 1))
    st.caption(f"Step {st.session_state.page + 1} of {len(pages)}")

    # HOME PAGE
    if st.session_state.page == 0:
       st.header("Usability Testing Tool")
       st.write("You are being invited to participate in a usability test. The goal is to evaluate and improve the design of our product. Your feedback will directly inform future development decisions.")
       st.write("The app is structured as follows:")
       st.markdown("""
                1. Intro 
                2. Consent From 
                3. Demographics 
                4. Tasks 
                5. Exit Questionnaire 
                6. Report 
                """)
       st.subheader("Before you begin:")
       st.markdown("""
              - This study will take approximately **5–10 minutes**
              - Your responses are completely anonymous
              """)
       st.info("When you are ready, click **Next** to review the consent form.")

    # CONSENT PAGE
    elif st.session_state.page == 1:
       st.header("Consent Form")

       st.subheader("Data Privacy & Anonymity")
       st.write(
          "All data collected during this study will remain strictly confidential. Your responses will be anonymized and will never be linked back to you personally. Data will only be used internally for product improvement purposes and will not be shared with any third parties.")

       data_types = pd.DataFrame({
          "Data Type": ["Task responses", "Survey answers", "Interaction data"],
          "Purpose": [
             "Measure usability and task success",
             "Understand user experience",
             "Identify design issues"
          ]
       })

       st.dataframe(data_types, hide_index=True)

       st.subheader("Right to Withdraw")
       st.write(
          "Your participation is entirely voluntary. You may stop at any time and for any reason without penalty or consequence. You are not obligated to complete the study once started.")
       st.divider()
       consent = st.checkbox("I have read and understood the above, and I agree to participate.")
       st.write("")
       if st.session_state.get("consent_attempted"):
          if not consent:
             st.warning("You must agree to the consent form to proceed.")
          else:
             st.success("Thank you for agreeing. You may proceed to the next section.")

    # DEMOGRAPHICS PAGE
    elif st.session_state.page == 2:
       st.header("Demographics")
       st.write("Please answer the following questions. All responses are anonymous.")
       col_a, col_b = st.columns([2, 3])
       with col_a:
          age = st.selectbox("Age range", ["", "18–24", "25–34", "35–44", "45–54", "55+"])
          gender = st.selectbox("Gender", ["", "Male", "Female", "Non-binary", "Other"])
          education = st.selectbox("Highest level of education",
                                   ["", "Prefer not to say", "High school", "Some college", "Bachelor's degree",
                                    "Graduate degree"])

       experience = st.pills("How would you rate your tech experience?",
                             options=["Beginner", "Basic", "Intermediate", "Advanced", "Expert"])

       st.divider()
       if st.button("Submit to Save Responses", use_container_width=True):
          if not all([age, gender, education, experience]):
             st.session_state.demo_attempted = True
          else:
             file = "responses.csv"
             file_exists = os.path.isfile(file)
             with open(file, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["age", "gender", "education", "experience"])
                if not file_exists:
                   writer.writeheader()
                writer.writerow({"age": age, "gender": gender, "education": education, "experience": experience})
             st.session_state.demo_saved = True
             st.session_state.demo_data = {"age": age, "gender": gender, "education": education, "experience": experience}
             st.success("Responses saved! You may now proceed to the next section.")

       if st.session_state.get("demo_attempted") and not st.session_state.get("demo_saved"):
          st.warning("Please complete all fields before submitting.")

    # TASKS PAGE
    elif st.session_state.page == 3:
       st.header("Task Page")
       st.write("Select a task, start the timer, and record your observations when finished.")
       st.divider()

       tasks = {
          "":"",
          "Task 1: Find a race": "Go into the application and find a race near your location, filter for 5k, and go into a race of your choice.",
          "Task 2: Register": "Find and interact with the registration button for a race of your liking",
          "Task 3: See map": "Look for races near a location and find where the map to display those locations is.",
       }

       if st.session_state.get("task_just_saved"):
          st.success("Task saved! You may proceed to the next section.")
          st.session_state.task_just_saved = False

       selected_task = st.selectbox("Select a task", options=list(tasks.keys()), key="selected_task")
       st.write(tasks[selected_task])

       if "task_status" not in st.session_state:
          st.session_state.task_status = "ready"

       with st.container(border=True):
          if st.session_state.task_status == "ready":
             if st.button("Start Timer", use_container_width=True, disabled=not selected_task):
                st.session_state.task_start_time = time.time()
                st.session_state.task_status = "in_progress"
                st.rerun()

          elif st.session_state.task_status == "in_progress":
             st.info("Timer running...")
             col_done, col_fail = st.columns(2)
             with col_done:
                if st.button("Finish", use_container_width=True):
                   st.session_state.task_duration = time.time() - st.session_state.task_start_time
                   st.session_state.task_outcome = "Completed"
                   st.session_state.task_status = "completed"
                   st.rerun()
             with col_fail:
                if st.button("Could Not Finish", use_container_width=True):
                   st.session_state.task_duration = time.time() - st.session_state.task_start_time
                   st.session_state.task_outcome = "Could Not Finish"
                   st.session_state.task_status = "completed"
                   st.rerun()

          elif st.session_state.task_status == "completed":
             # st.success(f"Outcome: {st.session_state.task_outcome}")
             st.caption(f"Completed in {st.session_state.task_duration:.2f} seconds")
             notes = st.text_area("Notes on your experience", key="task_notes", placeholder="Add any observations here...")

             if st.button("Save & Submit", use_container_width=True):
                data_dict = {
                   "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                   "task_name": selected_task,
                   "success": st.session_state.task_outcome,
                   "duration_seconds": round(st.session_state.task_duration, 2),
                   "notes": notes,
                }
                file = "task_data.csv"
                file_exists = os.path.isfile(file)
                with open(file, "a", newline="") as f:
                   writer = csv.DictWriter(f, fieldnames=["timestamp", "task_name", "success", "duration_seconds", "notes"])
                   if not file_exists:
                      writer.writeheader()
                   writer.writerow(data_dict)
                st.session_state.task_saved = True
                st.session_state.task_status = "ready"
                st.session_state.task_just_saved = True
                st.rerun()


    # EXIT QUESTIONNAIRE PAGE
    elif st.session_state.page == 4:
       st.header("Exit Questionnaire")
       st.write("Please share your feedback about the experience.")
       st.divider()

       st.subheader("Rate Your Experience")
       st.write("How would you rate your overall experience?")
       overall_rating = st.pills("Overall experience", options=["1 - Poor", "2 - Fair", "3 - Average", "4 - Good", "5 - Excellent"], label_visibility="collapsed", key="eq_overall")
       st.write("How easy was it to complete the tasks?")
       ease_rating = st.pills("Ease of tasks", options=["Very Difficult", "Difficult", "Neutral", "Easy", "Very Easy"], label_visibility="collapsed", key="eq_ease")

       st.divider()
       st.subheader("Tell Us More")
       liked_most = st.text_area("What did you like most about the experience?", key="eq_liked")
       would_improve = st.text_area("What would you improve?", key="eq_improve")
       additional_comments = st.text_area("Any additional comments?", key="eq_comments")

       st.divider()
       if st.button("Submit Questionnaire", use_container_width=True):
          if not all([overall_rating, ease_rating, liked_most.strip(), would_improve.strip(), additional_comments.strip()]):
             st.session_state.exit_attempted = True
          else:
             exit_row = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "overall_rating": overall_rating,
                "ease_of_tasks": ease_rating,
                "liked_most": liked_most,
                "would_improve": would_improve,
                "additional_comments": additional_comments,
             }
             file = "exit_questionnaire.csv"
             file_exists = os.path.isfile(file)
             with open(file, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=exit_row.keys())
                if not file_exists:
                   writer.writeheader()
                writer.writerow(exit_row)
             st.session_state.exit_data = exit_row
             st.session_state.exit_saved = True
             st.success("Questionnaire saved! You may now proceed to the summary.")

       if st.session_state.get("exit_attempted") and not st.session_state.get("exit_saved"):
          st.warning("Please answer all questions before submitting.")

    # SUMMARY PAGE
    elif st.session_state.page == 5:
       st.header("Report")
       st.write("Thank you for completing the study. Below is a summary of all participant responses.")
       st.divider()

       st.subheader("Demographics")
       if os.path.isfile("responses.csv"):
          demo_df = pd.read_csv("responses.csv")
          demo_df.columns = ["Age", "Gender", "Education", "Tech Experience"]
          st.dataframe(demo_df, use_container_width=True, hide_index=True)
       else:
          st.info("No demographic data recorded.")

       st.divider()
       st.subheader("Task Results")
       if os.path.isfile("task_data.csv"):
          expected_cols = ["timestamp", "task_name", "success", "duration_seconds", "notes"]
          task_df = pd.read_csv("task_data.csv")
          if list(task_df.columns) != expected_cols:
             task_df = pd.read_csv("task_data.csv", header=None, names=expected_cols)
          task_df["duration_seconds"] = pd.to_numeric(task_df["duration_seconds"], errors="coerce")
          # Assign participant numbers based on timestamp groups
          task_df["participant"] = task_df.groupby("timestamp").ngroup() + 1
          task_df["participant"] = "P" + task_df["participant"].astype(str)

          # Overview metrics per task
          task_names = task_df["task_name"].unique()
          overview_cols = st.columns(len(task_names))
          for i, name in enumerate(task_names):
             t = task_df[task_df["task_name"] == name]
             with overview_cols[i]:
                with st.container(border=True):
                   st.caption(name)
                   total = len(t)
                   completed = len(t[t["success"] == "Completed"])
                   rate = int((completed / total) * 100) if total > 0 else 0
                   st.metric("Success Rate", f"{rate}%")
                   st.metric("Avg Time", f"{t['duration_seconds'].mean():.1f}s")
                   st.metric("Participants", total)

          # Completion time comparison bar chart
          st.subheader("Average Completion Times")
          chart_data = task_df.groupby("task_name")["duration_seconds"].mean().round(1).reset_index()
          chart_data["task_label"] = chart_data["task_name"].str.extract(r"(Task \d+)")
          chart = alt.Chart(chart_data).mark_bar().encode(
             x=alt.X("task_label:N", title=None, sort=chart_data["task_label"].tolist()),
             y=alt.Y("duration_seconds:Q", title="Time (s)"),
             tooltip=["task_name", "duration_seconds"]
          ).properties(height=300)
          st.altair_chart(chart, use_container_width=True)

          # Per-task details in expanders
          st.subheader("Detailed Responses by Task")
          for name in task_names:
             t = task_df[task_df["task_name"] == name]
             with st.expander(name):
                detail_df = t[["participant", "timestamp", "success", "duration_seconds", "notes"]].copy()
                detail_df.columns = ["Participant", "Timestamp", "Outcome", "Duration (s)", "Notes"]
                st.dataframe(detail_df, use_container_width=True, hide_index=True)
       else:
          st.info("No task data recorded.")

       st.divider()
       st.subheader("Exit Questionnaire Responses")
       if os.path.isfile("exit_questionnaire.csv"):
          expected_exit_cols = ["timestamp", "overall_rating", "ease_of_tasks", "recommend_likelihood", "liked_most", "would_improve", "additional_comments"]
          exit_df = pd.read_csv("exit_questionnaire.csv")
          if list(exit_df.columns) != expected_exit_cols:
             exit_df = pd.read_csv("exit_questionnaire.csv", header=None, names=expected_exit_cols)

          exit_df["participant"] = "P" + (exit_df.index + 1).astype(str)

          st.write("**Ratings**")
          ratings_df = exit_df[["participant", "timestamp", "overall_rating", "ease_of_tasks", "recommend_likelihood"]].copy()
          ratings_df.columns = ["Participant", "Timestamp", "Overall Rating", "Ease of Tasks", "Recommend Likelihood"]
          st.dataframe(ratings_df, use_container_width=True, hide_index=True)

          st.write("**Satisfaction Distribution**")
          rating_order = ["1 - Poor", "2 - Fair", "3 - Average", "4 - Good", "5 - Excellent"]
          rating_counts = exit_df["overall_rating"].value_counts().reindex(rating_order, fill_value=0).reset_index()
          rating_counts.columns = ["Rating", "Count"]
          chart = alt.Chart(rating_counts).mark_bar().encode(
             x=alt.X("Rating:N", sort=rating_order, title=None),
             y=alt.Y("Count:Q", title="Participants"),
             tooltip=["Rating", "Count"]
          ).properties(height=300)
          st.altair_chart(chart, use_container_width=True)

          rating_map = {"1 - Poor": 1, "2 - Fair": 2, "3 - Average": 3, "4 - Good": 4, "5 - Excellent": 5}
          numeric_ratings = exit_df["overall_rating"].map(rating_map)
          avg_rating = numeric_ratings.mean()
          st.metric(label="Average Overall Rating", value=f"{avg_rating:.1f} / 5")

          st.write("**Open-Ended Responses**")
          open_df = exit_df[["participant", "timestamp", "liked_most", "would_improve", "additional_comments"]].copy()
          open_df.columns = ["Participant", "Timestamp", "Liked Most", "Would Improve", "Additional Comments"]
          st.dataframe(open_df, use_container_width=True, hide_index=True)
       else:
          st.info("No exit questionnaire data recorded.")


    col1, col2, col3 = st.columns([2, 6, 2])
    with col1:
       if st.session_state.page > 0:
          if st.button("← Back", use_container_width=True):
             st.session_state.page -= 1
             st.rerun()
    with col3:
       if st.session_state.page < len(pages) - 1:
          if st.button("Next →", use_container_width=True):
             if st.session_state.page == 1 and not consent:
                st.session_state.consent_attempted = True
                st.rerun()
             elif st.session_state.page == 2 and not st.session_state.get("demo_saved"):
                st.session_state.demo_attempted = True
                st.rerun()
             elif st.session_state.page == 3 and not st.session_state.get("task_saved"):
                st.rerun()
             elif st.session_state.page == 4 and not st.session_state.get("exit_saved"):
                st.session_state.exit_attempted = True
                st.rerun()
             else:
                st.session_state.consent_attempted = False
                st.session_state.page += 1
                st.rerun()