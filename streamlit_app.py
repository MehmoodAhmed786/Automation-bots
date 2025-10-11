import streamlit as st
import os
import time
import random
import tempfile
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import undetected_chromedriver as uc

# --- defaults (adjust if needed) ---
TIKTOK_URL = "https://www.tiktok.com/"

# --- helper functions (same logic as your script) ---
def load_cookies_from_txt(driver, path):
    """Load cookies in Netscape/cookies.txt format into Selenium driver."""
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.strip().split('\t')
            if len(parts) != 7:
                continue
            domain, flag, path_c, secure, expiry, name, value = parts
            cookie = {
                "domain": domain,
                "name": name,
                "value": value,
                "path": path_c,
                "secure": secure.lower() == "true",
            }
            if expiry.isdigit():
                cookie["expiry"] = int(expiry)
            try:
                driver.add_cookie(cookie)
            except Exception:
                # ignore cookies that can't be added
                pass

def get_cookie_files_from_dir(dir_path):
    if not os.path.exists(dir_path):
        return []
    files = []
    for fn in os.listdir(dir_path):
        if fn.lower().endswith(".txt"):
            files.append(os.path.join(dir_path, fn))
    return sorted(files)

def click_comment_icon(driver, comments_list, st_log):
    """Use the XPaths you provided to open comment box, type a random comment human-like and post."""
    time.sleep(3)  # wait for page & elements
    try:
        comment_btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[5]/div[2]/button[2]")
        ActionChains(driver).move_to_element(comment_btn).pause(1.2).click(comment_btn).perform()
        st_log.write("Clicked comment icon.")
        time.sleep(2)

        comment_box = driver.find_element(By.XPATH,
            "/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div/div/div[1]/div/div[1]")
        ActionChains(driver).move_to_element(comment_box).pause(0.8).click(comment_box).perform()
        time.sleep(0.8)

        if comments_list:
            comment = random.choice(comments_list)
        else:
            comment = "Nice video!"
        st_log.write(f"Selected comment: {comment}")

        # Type like a human
        actions = ActionChains(driver)
        for ch in comment:
            actions.send_keys(ch).perform()
            time.sleep(random.uniform(0.07, 0.16))

        time.sleep(0.8)
        post_btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div/div/div[2]")
        post_btn.click()
        st_log.write("Submitted the comment.")
        return True
    except NoSuchElementException:
        st_log.write("Comment elements not found on this page.")
        return False
    except ElementClickInterceptedException:
        st_log.write("Click intercepted; could not interact with element.")
        return False
    except Exception as e:
        st_log.write(f"Unexpected error while commenting: {e}")
        return False

# --- Streamlit UI ---
st.title("TikTok multi-account commenter (Streamlit)")

st.markdown("Provide accounts cookies (.txt), links and comments. The app will open each account and comment on each link.")

# Cookie input: either upload multiple files or point to local dir
use_upload = st.checkbox("Upload cookie .txt files (instead of reading a local folder)", value=False)

uploaded_cookie_files = []
cookie_dir_input = st.text_input("Local cookies folder path (if not uploading)", "cookies")
if use_upload:
    uploaded_cookie_files = st.file_uploader("Upload one or more cookie .txt files", type="txt", accept_multiple_files=True)

# Links input: either upload links.txt or paste
links_upload = st.file_uploader("Upload links.txt (optional)", type="txt")
links_text = st.text_area("Or paste links (one URL per line)", height=120)
if links_upload and not links_text:
    links_text = links_upload.getvalue().decode("utf-8")

# Comments input: either upload comments.txt or paste
comments_upload = st.file_uploader("Upload comments.txt (optional)", type="txt")
comments_text = st.text_area("Or paste comments (one comment per line)", height=120, key="comments_area")
if comments_upload and not comments_text:
    comments_text = comments_upload.getvalue().decode("utf-8")

# Options
max_accounts = st.number_input("Max accounts to process (0 = all)", min_value=0, value=0, step=1)
delay_between_links = st.slider("Base delay between links (seconds)", 2, 20, (6))

start_btn = st.button("Start commenting")

# helper to parse lists
def parse_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

# Execution
if start_btn:
    # Build links & comments lists
    links = parse_lines(links_text)
    if not links:
        st.error("No links provided. Paste links or upload links.txt.")
    else:
        comments = parse_lines(comments_text)

        # Prepare cookie files
        tmp_dir = None
        cookie_files = []
        if use_upload:
            if not uploaded_cookie_files:
                st.error("No cookie files uploaded.")
            else:
                tmp_dir = tempfile.mkdtemp(prefix="st_cookies_")
                for uf in uploaded_cookie_files:
                    dest = os.path.join(tmp_dir, uf.name)
                    with open(dest, "wb") as f:
                        f.write(uf.getvalue())
                    cookie_files.append(dest)
        else:
            cookie_files = get_cookie_files_from_dir(cookie_dir_input)

        if not cookie_files:
            st.error("No cookie .txt files found.")
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)
        else:
            if max_accounts > 0:
                cookie_files = cookie_files[:max_accounts]

            log_box = st.empty()
            logs = []

            def log(msg):
                timestamp = time.strftime("%H:%M:%S")
                logs.append(f"[{timestamp}] {msg}")
                log_box.text("\n".join(logs))

            # iterate accounts
            for idx, cookie_file in enumerate(cookie_files, start=1):
                account_name = os.path.splitext(os.path.basename(cookie_file))[0]
                log(f"=== Starting account {idx}/{len(cookie_files)}: {account_name} ===")
                driver = None
                try:
                    driver = uc.Chrome()
                    driver.maximize_window()
                    driver.get(TIKTOK_URL)
                    time.sleep(2)
                    load_cookies_from_txt(driver, cookie_file)
                    driver.refresh()
                    time.sleep(2)

                    for i, link in enumerate(links, start=1):
                        log(f"[{account_name}] Opening ({i}/{len(links)}): {link}")
                        try:
                            driver.get(link)
                            time.sleep(random.uniform(max(2, delay_between_links - 2), delay_between_links + 3))
                            ok = click_comment_icon(driver, comments, st_log=st.empty())
                            if ok:
                                log(f"[{account_name}] Comment posted on link {i}")
                            else:
                                log(f"[{account_name}] Comment NOT posted on link {i}")
                            time.sleep(random.uniform(4.0, 10.0))
                        except Exception as e:
                            log(f"[{account_name}] Error on link {i}: {e}")
                            time.sleep(2)
                except Exception as e:
                    log(f"Failed to start browser for {account_name}: {e}")
                finally:
                    if driver:
                        try:
                            driver.quit()
                        except Exception:
                            pass
                    log(f"=== Finished account: {account_name} ===")

            # cleanup uploaded tmp dir if used
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)

            st.success("Run finished. Check logs above.")