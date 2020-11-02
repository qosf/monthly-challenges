# QOSF Monthly Challenges

Repository containing monthly challenges in quantum computing.

## Challenge 01

**Link to Problem PDF**: [Challenge 01](./challenge-01/qosf-monthly-challenge-01.pdf)

**Release date**: November 2nd, 2020

**Submission deadline (optional):** November 23nd, 2020

## How it Works

These challenges will help you hone your general quantum computing skills by tackling some problems.

We release a new question every month. These are open to everybody and you're welcome to try your hand at solving them either individually or as a team.   
- You are free to use any framework that you like, and submit your solutions in any format. Just make sure they're easy to evaluate.

**You're also welcome to *contribute* challenge questions! Open an issue on this repo and describe the question, we'll take a look at it!** 

## Tentative Timeline

- We will try and release each challenge on the same date every month.
- You get a month's time to solve each question, but if you wish to have your solution reviewed please aim to submit your solution within the first 2 or 3 weeks.
- To avoid any confusion, please refrain from *submitting* solutions to old questions. You're welcome to try them out though!

## Submission

- Please fork this repository and use that to work on your solutions to the challenges. 
	- Follow the folder structure that you see here. For each challenge, create a directory in your repo called `challenge-xx`, where xx is the challenge number.
	- Under this directory, create a folder with your github username (all lowercase, separated-by-hyphens). Your solution goes into this directory.
- If you complete a challenge and want to "submit" your solution, raise a Pull Request (PR) from your repo to ours. 
- If your solutions works, we'll merge it to our repo.
- The best ones will be given a shout-out! 😃
- Note that if you're working as a team, it is sufficient to submit just one PR.

## Evaluation

- We want this to be a community driven project, so evaluation will be in the form of peer reviews.
- *Please* take some time to go through other solutions and provide your feedback! The only way this will work well is if we learn from each other. 
- If you like a solution, please leave an emoji reaction (a positive one!) on the PR. We will probably use this to pick the best submissions.
- We will also send out a poll where you can pick your favorite submission. Please vote!

## Communication

- Please join the Slack channel for the challenge, where you can ask any questions you might have: [#monthly-challenges](https://qosf.slack.com/archives/C01D2GB1DMM)

## Git FAQ

- We recommend you install the new [GitHub CLI tool](https://cli.github.com/) which is pretty cool. 
- Forking: https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/fork-a-repo
	- Pro tip: If you're using the CLI we just told you about, you can do this without ever leaving the terminal! Run `gh repo fork qosf/monthly-challenges`. When asked if you want to clone the repository, hit `n`.
- Cloning (first time setup):  
  - ```git clone htps://github.com/{{your-github-username}}/monthly-challenges.git```
    - If you're using the CLI, just run  ```gh repo clone {{your-github-username}}/monthly-challenges```.
  - run `git remote add upstream https://github.com/qosf/monthly-challenges.git`. You **DO NOT** have to do this if you used the CLI to clone your repo (it does that automatically).
  - run ```git checkout main```
-  What to do before starting a new challenge:
   - Bring your fork on-par with our repo
		```
		git fetch upstream
		git checkout main
		git merge main upstream/main
		git push
		```
   - Create a branch to work on the new challenge
      - `git branch -b {{branch name}}`
- Work on the challenge (make sure your changes are all on the right branch).
- Periodically push your changes to your fork
   - `git push -u origin {{branch name}}` the first time you push. For subsequent pushes, just `git push`.
- Raising a Pull Request: https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/proposing-changes-to-your-work-with-pull-requests
  

Any other questions? Try the [GitHub documentation](https://docs.github.com/en) or ping us on Slack!
