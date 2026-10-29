# How to make a xkeyboard-config release

### Prerequisites

- Have write access to xkeyboard-config Git repositories.

### Steps

#### Prepare the translations

**2 weeks before release:**

- [ ] Create a release branch: `git checkout -b release/MAJOR.PREV_MINOR.99 master`
  where `MAJOR.PREV_MINOR` is the *last* released version.

- [ ] Bump the `version` in `meson.build` to `MAJOR.PREV_MINOR.99`.

- [ ] Run `meson setup buildddir; meson dist -C builddir` to make sure the release is good to go.

- [ ] Run `meson compile -C builddir xkeyboard-config-pot` to update `po/xkeyboard-config.pot` file.

- [ ] Commit `meson.build` and `po/xkeyboard-config.pot` with subject “String freeze MAJOR.MINOR”.

- [ ] Create a pull request with subject “String freeze MAJOR.MINOR” and
  description:

  > Bump version to send to the [Translation Project]
  > [Translation Project]: https://translationproject.org/html/maintainers.html

  and ensure *all* CI is green.

- [ ] Merge the pull request.

- [ ] Send `po/xkeyboard-config.pot` and `builddir/meson-dist/xkeyboard-config-MAJOR.PREV_MINOR.tar.xz` to Translation Project asking for translations update: <coordinator@translationproject.org>. See the [instructions from the TP].

[instructions from the TP]: https://translationproject.org/html/maintainers.html

- [ ] Give the Translation Project *2 weeks* to update translations.

#### Translations update

**Day of the release**

- [ ] Pull the latest [translation files] from Translation Project by executing
  `scripts/pull_translations.sh`.

- [ ] Trim any superfluous white space from these files.

- [ ] `git commit -m 'Update translations – Thanks to TP'`.

- [ ] Create a pull request with suject “Update translations”
  and ensure *all* CI is green.

- [ ] Merge the pull request.

[translation files]: https://translationproject.org/domain/xkeyboard-config.html

#### Release

- [ ] Ensure there is no issue in the tracker blocking the release. Make sure
  they have their milestone set to the relevant release and the relevant tag
  “critical”.

- [ ] Ensure all items in the current milestone are processed. Remaining items
  must be *explicitly* postponed by changing their milestone.

- [ ] Create a release branch: `git checkout -b release/MAJOR.MINOR master`.

- [ ] Bump the `version` in `meson.build`.

- [ ] Update the `ChangeLog.md` file for the release, following
  [the corresponding instructions](changes/README.md).

- [ ] Review the changelog: typos, item order, formatting.

- [ ] Run `meson setup buildddir; meson dist -C builddir` to make sure the release is good to go.

- [ ] Commit `git commit -m 'New version MAJOR.MINOR'`.

- [ ] Create a pull request using this template and ensure *all* CI is green.

- [ ] Merge the pull request.

- [ ] Tag:

  ```bash
  git switch master && \
  git pull && \
  git tag --annotate -m "xkeyboard-config-<MAJOR.MINOR>" "xkeyboard-config-<MAJOR.MINOR>"
  ```

- [ ] Push the tag `git push origin xkeyboard-config-<MAJOR.MINOR>`.

- [ ] Create a Gitlab release:

  1. [Go to the new release page](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/releases/new).
  2. Select the newly created tag.
  3. Leave the “Release title” field blank.
  4. Select the corresponding milestone.
  5. Select the date that the tag was pushed.
  6. Leave the “Release notes” field blank.
  7. Add the link to the corresponding (future) blog post.

- [ ] Edit the release to add a link to the announcement email
  from the xorg-announce@lists.x.org mailing list archive.

#### Send announcement email to xorg-announce

- [ ] Send an email to the xorg-announce@lists.x.org mailing list, using this template:

```
Subject: [ANNOUNCE] xkeyboard-config MAJOR.MINOR

<NEWS & comments for this release>

Git tag:
--------

git tag: xkeyboard-config-<MAJOR.MINOR>
git commit: <git commit sha>

Tarballs:
---------

https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/releases/xkeyboard-config-MAJOR.MINOR

<YOUR NAME>
```
