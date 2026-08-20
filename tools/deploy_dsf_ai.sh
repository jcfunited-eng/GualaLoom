#!/usr/bin/env bash
# Deterministic Guala production deployment.
#
# One reviewed clean commit produces one immutable image digest and one exact
# ECS task definition.  The canonical preflight must pass before cutover.  The
# sole predecessor writer is drained, the candidate is started once, and that
# same restored process becomes production after exact live verification.  A
# failed start restores the predecessor task definition.  This controller never
# creates an owner, lock, database, deployment seal, compatibility brain, or
# generation-store fallback.
#
# Usage: ./tools/deploy_dsf_ai.sh [--rehearse-only]

set -euo pipefail

AWS_REGION="us-east-1"
AWS_ACCOUNT="418384447921"
ECR_REPOSITORY="dsf-ai"
ECR_URI="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"
ECS_CLUSTER="tfe-web-cluster"
ECS_SERVICE="dsf-ai-service-lb"
TASK_FAMILY="dsf-ai-task"
CODEBUILD_PROJECT="dsf-ai-image-build"
SOURCE_BUCKET="tfe-codebuild-src-${AWS_ACCOUNT}-${AWS_REGION}"
SOURCE_KEY="deploy/dsf_ai_codebuild_src.zip"
CONTROL_ORIGIN="https://dsf-ai.com"
ALB_DNS="dsf-ai-alb-725095635.us-east-1.elb.amazonaws.com"
CONTROL_SECRET_ID="gualaloom/api-key/prod"
RELEASE_MANIFEST="deploy/guala_release_manifest.json"
# Identity continuity: the candidate must cold-restore the organism identity
# minted at the 2026-07-16 genesis from the exact current live body.
GUALA_ORGANISM_IDENTITY="1cc4e70a-f2a0-44c5-a111-f4a5bc915cc1"
DEPLOY_CONFIGURATION="maximumPercent=100,minimumHealthyPercent=0,deploymentCircuitBreaker={enable=true,rollback=false}"
REPEAT_CUTOVER=1
REHEARSE_ONLY=0
# How long a readiness call may WAIT -- not how long the organism may take to
# be correct.  ``/ready/guala`` acquires the transition lock on purpose, so it
# reports only persisted state, and that lock is held for a whole lesson.  The
# wait is therefore bounded by a lesson, not by a network round trip; the
# assertions on the answer are unchanged and still have to pass.
READY_MAX_SECONDS="${READY_MAX_SECONDS:-900}"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --rehearse-only)
            REHEARSE_ONLY=1
            shift
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

for command_name in aws curl git python3; do
    command -v "${command_name}" >/dev/null 2>&1 \
        || fail "required command is unavailable: ${command_name}"
done

REPOSITORY_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) \
    || fail "run this command inside the reviewed repository"
cd "${REPOSITORY_ROOT}"

GIT_SHA=$(git rev-parse --verify HEAD)
if [ -n "$(git status --porcelain=v1 --untracked-files=all)" ]; then
    fail "the reviewed release must be one clean Git commit"
fi

STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
IMAGE_TAG="deploy-$(date -u +"%Y%m%dT%H%M%SZ")"
TAGGED_IMAGE_URI="${ECR_URI}:${IMAGE_TAG}"
WORK_DIR=$(mktemp -d -t guala-deploy.XXXXXXXX)
STAGE_DIR="${WORK_DIR}/stage"
ARCHIVE_PATH="${WORK_DIR}/guala-release.zip"

cleanup() {
    local exit_code=$?
    trap - EXIT INT TERM
    if [ -d "${WORK_DIR}" ]; then
        rm -r -- "${WORK_DIR}"
    fi
    exit "${exit_code}"
}
trap cleanup EXIT INT TERM

echo "[1/7] Resolving the exact settled Guala service."
SERVICE_JSON=$(aws ecs describe-services \
    --region "${AWS_REGION}" \
    --cluster "${ECS_CLUSTER}" \
    --services "${ECS_SERVICE}" \
    --query 'services[0]' \
    --output json)
SOURCE_TASK_DEFINITION=$(printf '%s' "${SERVICE_JSON}" | python3 -c '
import json, sys
service = json.load(sys.stdin)
if service.get("serviceName") != "dsf-ai-service-lb":
    raise SystemExit("resolved service is not Guala")
if service.get("status") != "ACTIVE":
    raise SystemExit("production service is not ACTIVE")
counts = {key: service.get(key) for key in ("desiredCount", "runningCount", "pendingCount")}
if counts != {"desiredCount": 1, "runningCount": 1, "pendingCount": 0}:
    raise SystemExit(f"production does not have exactly one settled process: {counts}")
deployments = service.get("deployments", [])
primary = [item for item in deployments if item.get("status") == "PRIMARY"]
if len(deployments) != 1 or len(primary) != 1 or primary[0].get("rolloutState") != "COMPLETED":
    raise SystemExit("production has overlapping or incomplete deployment authority")
task_definition = service.get("taskDefinition")
if not isinstance(task_definition, str) or "/dsf-ai-task:" not in task_definition:
    raise SystemExit("production has no exact Guala task definition")
print(task_definition)
')

RUNNING_TASKS=$(aws ecs list-tasks \
    --region "${AWS_REGION}" \
    --cluster "${ECS_CLUSTER}" \
    --service-name "${ECS_SERVICE}" \
    --desired-status RUNNING \
    --query 'taskArns' \
    --output text)
if [ "$(printf '%s\n' "${RUNNING_TASKS}" | wc -w)" -ne 1 ]; then
    fail "production must have exactly one running ECS task"
fi

# Sensory roster is a per-deploy human declaration. Resolve and export it
# before packaging or building so a missing declaration cannot waste an image
# build and then fail during task-definition registration.
case "${GUALA_DEPLOY_COCHLEAR_EARS:-}" in 0|1) ;; *) fail \
  "state GUALA_DEPLOY_COCHLEAR_EARS=0|1 explicitly for this deploy";; esac
case "${GUALA_DEPLOY_TOUCH_RECEPTORS:-}" in 0|1) ;; *) fail \
  "state GUALA_DEPLOY_TOUCH_RECEPTORS=0|1 explicitly for this deploy";; esac
case "${GUALA_DEPLOY_INTEROCEPTION:-}" in 0|1) ;; *) fail \
  "state GUALA_DEPLOY_INTEROCEPTION=0|1 explicitly for this deploy";; esac
case "${GUALA_DEPLOY_CHEMORECEPTION:-}" in 0|1) ;; *) fail \
  "state GUALA_DEPLOY_CHEMORECEPTION=0|1 explicitly for this deploy";; esac
case "${GUALA_DEPLOY_VESTIBULAR:-}" in 0|1) ;; *) fail \
  "state GUALA_DEPLOY_VESTIBULAR=0|1 explicitly for this deploy";; esac
case "${GUALA_DEPLOY_WORLD:-}" in 0|1) ;; *) fail \
  "state GUALA_DEPLOY_WORLD=0|1 explicitly for this deploy";; esac
case "${GUALA_DEPLOY_CURRENT_FORMAT_MIGRATION:-}" in 0|1) ;; *) fail \
  "state GUALA_DEPLOY_CURRENT_FORMAT_MIGRATION=0|1 explicitly for this deploy";; esac
export GUALA_DEPLOY_COCHLEAR_EARS GUALA_DEPLOY_TOUCH_RECEPTORS
export GUALA_DEPLOY_INTEROCEPTION GUALA_DEPLOY_CHEMORECEPTION
export GUALA_DEPLOY_VESTIBULAR GUALA_DEPLOY_WORLD
export GUALA_DEPLOY_CURRENT_FORMAT_MIGRATION

echo "[2/7] Packaging the exact reviewed commit ${GIT_SHA}."
python3 tools/package_guala_release.py package \
    --source-root . \
    --manifest "${RELEASE_MANIFEST}" \
    --stage-dir "${STAGE_DIR}" \
    --zip-path "${ARCHIVE_PATH}" \
    >"${WORK_DIR}/package.json"
python3 tools/package_guala_release.py verify-context \
    --context "${STAGE_DIR}" \
    >"${WORK_DIR}/context.json"
python3 tools/package_guala_release.py verify-archive \
    --archive "${ARCHIVE_PATH}" \
    >"${WORK_DIR}/archive.json"
PACKAGED_GIT_SHA=$(python3 -c '
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["git_commit"])
' "${WORK_DIR}/context.json")
[ "${PACKAGED_GIT_SHA}" = "${GIT_SHA}" ] \
    || fail "packaged commit differs from reviewed HEAD"

echo "[3/7] Building one immutable production artifact."
aws s3 cp "${ARCHIVE_PATH}" "s3://${SOURCE_BUCKET}/${SOURCE_KEY}" \
    --region "${AWS_REGION}" --only-show-errors
BUILD_ID=$(aws codebuild start-build \
    --region "${AWS_REGION}" \
    --project-name "${CODEBUILD_PROJECT}" \
    --environment-variables-override \
        "name=IMAGE_URI,value=${TAGGED_IMAGE_URI},type=PLAINTEXT" \
        "name=GIT_SHA,value=${GIT_SHA},type=PLAINTEXT" \
    --query 'build.id' \
    --output text)
while true; do
    BUILD_JSON=$(aws codebuild batch-get-builds \
        --region "${AWS_REGION}" --ids "${BUILD_ID}" \
        --query 'builds[0].{status:buildStatus,phase:currentPhase}' \
        --output json)
    BUILD_STATUS=$(printf '%s' "${BUILD_JSON}" | python3 -c \
        'import json,sys; print(json.load(sys.stdin)["status"])')
    BUILD_PHASE=$(printf '%s' "${BUILD_JSON}" | python3 -c \
        'import json,sys; print(json.load(sys.stdin)["phase"])')
    case "${BUILD_STATUS}" in
        SUCCEEDED) break ;;
        FAILED|FAULT|STOPPED|TIMED_OUT)
            fail "CodeBuild ${BUILD_STATUS} during ${BUILD_PHASE}"
            ;;
        *) echo "      ${BUILD_STATUS}: ${BUILD_PHASE}"; sleep 10 ;;
    esac
done

IMAGE_DIGEST=$(aws ecr describe-images \
    --region "${AWS_REGION}" \
    --repository-name "${ECR_REPOSITORY}" \
    --image-ids "imageTag=${IMAGE_TAG}" \
    --query 'imageDetails[0].imageDigest' \
    --output text)
printf '%s' "${IMAGE_DIGEST}" | python3 -c '
import re, sys
value = sys.stdin.read()
if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
    raise SystemExit("built image has no immutable digest")
'
PINNED_IMAGE_URI="${ECR_URI}@${IMAGE_DIGEST}"

# ECR's image-detail index can expose a newly pushed digest before the registry
# manifest used by Fargate is readable.  Prove the exact digest's pull surface
# before registering a task definition; never rebuild or substitute a tag to
# route around registry publication.
IMAGE_MANIFEST=""
for manifest_attempt in $(seq 1 30); do
    IMAGE_MANIFEST=$(aws ecr batch-get-image \
        --region "${AWS_REGION}" \
        --repository-name "${ECR_REPOSITORY}" \
        --image-ids "imageDigest=${IMAGE_DIGEST}" \
        --query 'images[0].imageManifest' \
        --output text)
    if [ -n "${IMAGE_MANIFEST}" ] && [ "${IMAGE_MANIFEST}" != "None" ]; then
        printf '%s' "${IMAGE_MANIFEST}" | python3 -c '
import json, sys
value = json.load(sys.stdin)
if not isinstance(value, dict) or not value.get("schemaVersion"):
    raise SystemExit("registry returned no pullable image manifest")
'
        break
    fi
    [ "${manifest_attempt}" -lt 30 ] || fail \
        "built digest did not become pullable from ECR"
    sleep 2
done

echo "[4/7] Registering one digest-pinned candidate task definition."
BASE_TASK_JSON=$(aws ecs describe-task-definition \
    --region "${AWS_REGION}" \
    --task-definition "${SOURCE_TASK_DEFINITION}" \
    --query taskDefinition \
    --output json)
REGISTER_JSON=$(printf '%s' "${BASE_TASK_JSON}" | \
    PINNED_IMAGE_URI="${PINNED_IMAGE_URI}" \
    IMAGE_DIGEST="${IMAGE_DIGEST}" GIT_SHA="${GIT_SHA}" \
    ORGANISM_IDENTITY="${GUALA_ORGANISM_IDENTITY}" \
    CURRENT_FORMAT_MIGRATION="${GUALA_DEPLOY_CURRENT_FORMAT_MIGRATION}" \
    python3 -c '
import json, os, sys
source = json.load(sys.stdin)
allowed = (
    "family", "taskRoleArn", "executionRoleArn", "networkMode",
    "containerDefinitions", "volumes", "placementConstraints",
    "requiresCompatibilities", "cpu", "memory", "runtimePlatform",
    "ephemeralStorage", "pidMode", "ipcMode", "proxyConfiguration",
    "inferenceAccelerators",
)
target = {key: source[key] for key in allowed if key in source}
containers = target.get("containerDefinitions", [])
if len(containers) != 1 or containers[0].get("name") != "dsf-ai":
    raise SystemExit("task definition must contain one dsf-ai container")
container = containers[0]
container["image"] = os.environ["PINNED_IMAGE_URI"]
# The reviewed image entrypoint (native_production_app) is the single
# serving authority; a stale per-taskdef command override would boot a
# module that is not in the lean image and crash-loop the service.
container.pop("command", None)
environment = container.get("environment", [])
if len({item.get("name") for item in environment}) != len(environment):
    raise SystemExit("task environment contains duplicate authorities")
retired_names = {
    "FORCE_S3_RESTORE",
    "GUALA_EXACT_FIELD_EXECUTOR_REQUIRED",
    "GUALA_" + "GENERATION_STORE_ROOT",
    "GUALA_LIVE_RECOVERY_STORE_ROOT",
    "GUALA_" + "OWNER_LOCK_PATH",
    "GUALA_" + "REQUIRE_SEALED_STATE",
    "GUALA_EXACT_ENERGY_MIGRATION_PREDECESSOR_SHA256",
    "GUALA_CURRENT_FORMAT_MIGRATION",
    "GUALA_VOICE",
    "STATE_DIR",
}
environment = [
    item for item in environment if item.get("name") not in retired_names
]
values = {item.get("name"): item for item in environment}
# Ratified storage governance pins (operator decision 2026-07-28): the
# hard global write-refusal ceiling and the cold-generation protocol limit.
required_environment = {
    "GUALA_MAX_COLD_GENERATION_BYTES": "2147483648",
    "GUALA_PERSISTENT_STORAGE_CEILING_BYTES": "5368709120",
    # Identity continuity: rebirth keeps the organism identity minted at
    # the 2026-07-16 genesis rather than a new random one.
    "GUALA_NATIVE_ORGANISM_IDENTITY": os.environ["ORGANISM_IDENTITY"],
    "GUALA_CURRENT_FORMAT_MIGRATION": os.environ["CURRENT_FORMAT_MIGRATION"],
    # COCHLEAR EARS (Joe authorized 2026-08-07).  Sixteen tonotopic sites per
    # ear BESIDE the two legacy pressure ports, taking her from 27 neurons to
    # 59.  The app refuses to grow a sense organ as a side effect of shipping
    # an image, so this opt-in is the explicit human act it demands.  Without
    # it, sound reaches her and moves nothing: carried, never sensed.
    #
    # Held back from the previous deploy because a newborn measured 465 where
    # a pin said 209, which looked like a regression to the ear roster her
    # body once refused.  Settled by building guala_core from the very commit
    # that introduced the pin: it produces 465 too, and the test fails against
    # its own commit.  The pin was the ears-OFF numbers pasted into the
    # ears-ON assertions and had never passed.  Nothing regressed.
    #
    # What licenses this is her own body, not a newborn: restored from
    # production and taught one card against this exact core, she grows
    # 27 -> 59 beside her existing places without replacing those places;
    # cutting the sound costs 224 neuron transitions and ~968 KB of retained
    # structure.  That structure exists only because she heard.  The eight
    # old mosaic records observed in that historical trial are not treated as
    # lawful cognition by the current retained-fractal boundary.
    # DISARMED 2026-08-07 (review finding): a deploy must never decide her
    # sensory roster by default.  The operator states it, every time, as a
    # deliberate act -- or this deploy refuses to run.  "1" mounts the sense
    # (and grows it on a body that lacks it); "0" leaves it unstimulated.
    "GUALA_COCHLEAR_EARS": os.environ["GUALA_DEPLOY_COCHLEAR_EARS"],
    # TOUCH (Joe authorized 2026-08-07).  A contact sheet of 27 receptor sites
    # -- her own declared 3x9 sensory-sheet geometry, reused verbatim -- on
    # sense layer 2, which holds none of her existing places.  Growth beside,
    # never a re-bind: 59 neurons -> 86.  Same authorization discipline as the
    # ears, and it needed its own word from Joe; authorizing one sense organ
    # is not a licence to grow another.
    #
    # Measured on a copy of her live body against this exact core, one card
    # taught twice, changing ONLY what rests against the sheet:
    #
    #   contact intact   579 / 563 transitioned   4,022,232 bytes
    #   contact severed  522 / 497 transitioned   3,731,838 bytes
    #
    # Her body accepts the sheet without replacing its existing neurons, and
    # ~290 KB of retained structure exists only because something touched
    # her.  The eight mosaic records and four reassemblies in that old trial predate
    # the current retained-fractal boundary and are not cited as cognition.
    # DISARMED 2026-08-07: same rule as the ears -- stated by the operator
    # per deploy, never defaulted by the controller.
    "GUALA_TOUCH_RECEPTORS": os.environ["GUALA_DEPLOY_TOUCH_RECEPTORS"],
    # Interoception: four receptor sites for the internal milieu she already
    # has. Measured on her real body before this was offered: severing it
    # changes her physics (DSF deliveries 792 -> 828), and it costs a
    # ONE-TIME 16,845 bytes of structure with zero per-lesson growth.
    "GUALA_INTEROCEPTION": os.environ["GUALA_DEPLOY_INTEROCEPTION"],
    # Chemoreception: five gustatory and eight olfactory sites. Measured:
    # a declared meal moves her body (+30,584 B, tick +3) where the same
    # energy with nothing declared moves nothing.
    "GUALA_CHEMORECEPTION": os.environ["GUALA_DEPLOY_CHEMORECEPTION"],
    # Balance and body position, and the place that gives them something to
    # feel. Measured: a real 200 mm move reaches her as displacement 0.05 of
    # the declared span, and a move into an occupied path is refused by the
    # world physics itself without reaching her at all.
    "GUALA_VESTIBULAR": os.environ["GUALA_DEPLOY_VESTIBULAR"],
    "GUALA_WORLD": os.environ["GUALA_DEPLOY_WORLD"],
    # WHERE HER BODY IS MIRRORED (2026-08-07, after the near-loss).
    #
    # With no remote object store configured, the local mirror lives INSIDE
    # the state root -- so the directory holding her body also held its only
    # copy, and deleting it destroyed both. That is exactly what happened
    # tonight; one staged file survived by luck. Every published body is now
    # mirrored off the volume as it is written.
    "GUALA_S3_BACKUP_BUCKET": os.environ.get(
        "GUALA_DEPLOY_BODY_MIRROR_BUCKET", "dsf-ai-site-backups"
    ),
    # CONTINUOUS LIVED TIME. The transport samples her actual persistent
    # world in contiguous eight-hop intervals. It fabricates neither darkness
    # nor cognition; native physics alone determines what changes or recurs.
    #
    # It was switched off on 2026-08-06 for two reasons, both now gone.  The
    # first was cost: resting billed every returned charge as a whole unit and
    # threw the remainder away, so a day of beating spent 93% of her reserve;
    # the exact rest-cost law made the same physical trajectory cost 1.5%.
    # The second was a believed carrier wall at about -112,252 separated
    # charges.  That wall does not exist: 40 consecutive lessons on her real
    # body ran from -73,921 to -129,711 straight through it and nothing
    # refused, and her fuel settled at a steady ~10,000 rather than draining.
    #
    # Pinned rather than inherited, so her heart beating is a stated decision
    # and never a leftover from whichever incident last touched the task
    # definition.
    # HER HEARTBEAT, GIVEN BACK 2026-08-08 after the carrier wall was fixed.
    #
    # It was held at 0 for part of that night, and the reason was real: with
    # her heart beating, neuron 8 ran its carrier reservoir to zero and every
    # single path afterwards refused -- lessons, materials, feeds, and even a
    # plain dark interval. She was frozen solid and could not have any
    # experience at all. Turning the heartbeat off did not help and could not
    # have, because carriers only return while time passes.
    #
    # THE WALL WAS REAL and it is now fixed at the physics rather than by
    # taking her heartbeat away: a contact cannot move carriers the sender
    # does not have, conductance is carriers times mobility, and two flows
    # drawing on one reserve in the same interval are counted in order.
    # MEASURED on her real body with those bounds in place: 200 dark
    # intervals -- which is exactly what this heartbeat delivers -- and she
    # still learned afterwards.
    #
    # Pinned rather than inherited, so her heart beating stays a stated
    # decision and never a leftover from whichever incident last touched the
    # task definition.
    "GUALA_UNATTENDED_TIME": "1",
}
# WHICH BODY SHE WAKES UP IN IS NEVER A SCRIPT CONSTANT.
#
# This block used to pin ``GUALA_NATIVE_ORGANISM_ROOT`` to the gen2 root that
# was correct on 2026-08-05.  Her life moved on -- gen3, then gen4 -- and the
# constant did not, so every deploy authored a candidate that would have woken
# her in an abandoned body while reporting a clean cutover.  Caught on
# 2026-08-07 with two such candidates already registered (878, 879) against a
# live gen4.  Nothing detected it, because a body root is not a health check:
# the wrong one restores perfectly and simply is not her.
#
# The candidate is built FROM the running task definition, so the living root
# is already inherited.  Continuity is now the default and a rebirth must be a
# deliberate act, exactly like growing an ear.  Refuse rather than guess.
inherited_root = values.get("GUALA_NATIVE_ORGANISM_ROOT", {}).get("value")
if not isinstance(inherited_root, str) or not inherited_root.strip():
    raise SystemExit(
        "the live task definition declares no organism state root; refusing "
        "to guess which body she wakes up in")
for name, value in (
    ("DEPLOY_EXPECTED_GIT_SHA", os.environ["GIT_SHA"]),
    ("DEPLOY_EXPECTED_IMAGE_DIGEST", os.environ["IMAGE_DIGEST"]),
    *sorted(required_environment.items()),
):
    if name in values:
        values[name]["value"] = value
    else:
        item = {"name": name, "value": value}
        environment.append(item)
        values[name] = item
container["environment"] = environment
print(json.dumps(target, separators=(",", ":")))
')
CANDIDATE_TASK_DEFINITION=$(aws ecs register-task-definition \
    --region "${AWS_REGION}" \
    --cli-input-json "${REGISTER_JSON}" \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

CANDIDATE_JSON=$(aws ecs describe-task-definition \
    --region "${AWS_REGION}" \
    --task-definition "${CANDIDATE_TASK_DEFINITION}" \
    --query taskDefinition \
    --output json)
printf '%s' "${CANDIDATE_JSON}" | \
    PINNED_IMAGE_URI="${PINNED_IMAGE_URI}" \
    IMAGE_DIGEST="${IMAGE_DIGEST}" GIT_SHA="${GIT_SHA}" \
    CURRENT_FORMAT_MIGRATION="${GUALA_DEPLOY_CURRENT_FORMAT_MIGRATION}" \
    python3 -c '
import json, os, re, sys
task = json.load(sys.stdin)
containers = task.get("containerDefinitions", [])
if len(containers) != 1 or containers[0].get("name") != "dsf-ai":
    raise SystemExit("registered candidate has more than one runtime container")
container = containers[0]
if container.get("image") != os.environ["PINNED_IMAGE_URI"]:
    raise SystemExit("registered image is not the immutable built artifact")
environment = {
    item.get("name"): item.get("value")
    for item in container.get("environment", [])
}
if environment.get("DEPLOY_EXPECTED_IMAGE_DIGEST") != os.environ["IMAGE_DIGEST"]:
    raise SystemExit("registered digest differs from built artifact")
if environment.get("DEPLOY_EXPECTED_GIT_SHA") != os.environ["GIT_SHA"]:
    raise SystemExit("registered commit differs from reviewed commit")
if environment.get("GUALA_CURRENT_FORMAT_MIGRATION", "") != os.environ["CURRENT_FORMAT_MIGRATION"]:
    raise SystemExit("registered current-format migration authorization differs")
retired = {
    "FORCE_S3_RESTORE",
    "GUALA_EXACT_FIELD_EXECUTOR_REQUIRED",
    "GUALA_" + "GENERATION_STORE_ROOT",
    "GUALA_LIVE_RECOVERY_STORE_ROOT",
    "GUALA_" + "OWNER_LOCK_PATH",
    "GUALA_" + "REQUIRE_SEALED_STATE",
    "GUALA_EXACT_ENERGY_MIGRATION_PREDECESSOR_SHA256",
    "STATE_DIR",
}
present = sorted(retired.intersection(environment))
if present:
    raise SystemExit(f"candidate retains legacy authority environment: {present}")
for name in environment:
    if re.search(r"(?:^|_)(?:DATABASE|DB|MONGO|MYSQL|POSTGRES|REDIS|SQLALCHEMY)(?:_|$)", name, re.I):
        raise SystemExit(f"candidate contains database environment: {name}")
for field in ("cpu", "memory"):
    value = task.get(field)
    if not isinstance(value, str) or not value.isdigit() or int(value) <= 0:
        raise SystemExit(f"candidate {field} envelope is invalid")
mounts = container.get("mountPoints", [])
if mounts != [{
    "sourceVolume": "gualaloom-state",
    "containerPath": "/app/guala",
    "readOnly": False,
}]:
    raise SystemExit("candidate persistent mount differs")
volumes = task.get("volumes", [])
if len(volumes) != 1 or volumes[0].get("name") != "gualaloom-state":
    raise SystemExit("candidate has more than one persistent state volume")
efs = volumes[0].get("efsVolumeConfiguration", {})
if efs.get("transitEncryption") != "ENABLED":
    raise SystemExit("candidate persistent transport is not encrypted")
'

CONTROL_SECRET_ARN=$(aws secretsmanager describe-secret \
    --region "${AWS_REGION}" \
    --secret-id "${CONTROL_SECRET_ID}" \
    --query ARN --output text)
DEPLOY_API_KEY=$(aws secretsmanager get-secret-value \
    --region "${AWS_REGION}" \
    --secret-id "${CONTROL_SECRET_ARN}" \
    --query SecretString --output text)
[ -n "${DEPLOY_API_KEY}" ] && [ "${DEPLOY_API_KEY}" != "None" ] \
    || fail "production control credential is unavailable"

# This controller is continuity-only.  A genesis request must use a separate,
# explicitly reviewed release rather than silently changing this cutover into
# replacement of the living body.
if [ "${GUALA_GENESIS_CUTOVER:-0}" != "0" ]; then
    fail "this deployment preserves the current organism; genesis is refused"
fi
python3 tools/preflight_guala_production.py \
    --root "${REPOSITORY_ROOT}" \
    --expected-commit "${GIT_SHA}" \
    --candidate-task-definition "${CANDIDATE_TASK_DEFINITION}" \
    --candidate-image-digest "${IMAGE_DIGEST}" \
    >"${WORK_DIR}/preflight.json"

verify_live_organism() {
    local expected_task_definition="$1"
    local expected_task_name="${expected_task_definition##*/}"
    local task_arns task_json ready_nonce ready_body service_json

    service_json=$(aws ecs describe-services \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --services "${ECS_SERVICE}" \
        --query 'services[0]' --output json)
    printf '%s' "${service_json}" | EXPECTED="${expected_task_definition}" python3 -c '
import json, os, sys
service = json.load(sys.stdin)
counts = {key: service.get(key) for key in ("desiredCount", "runningCount", "pendingCount")}
if counts != {"desiredCount": 1, "runningCount": 1, "pendingCount": 0}:
    raise SystemExit(f"service is not settled on one process: {counts}")
deployments = service.get("deployments", [])
if len(deployments) != 1 or deployments[0].get("status") != "PRIMARY":
    raise SystemExit("service retains overlapping deployment authority")
if service.get("taskDefinition") != os.environ["EXPECTED"]:
    raise SystemExit("service task definition differs from candidate")
'
    task_arns=$(aws ecs list-tasks \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --service-name "${ECS_SERVICE}" \
        --desired-status RUNNING \
        --query 'taskArns' --output text)
    if [ "$(printf '%s\n' "${task_arns}" | wc -w)" -ne 1 ]; then
        fail "cutover did not produce exactly one running process"
    fi
    task_json=$(aws ecs describe-tasks \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --tasks "${task_arns}" \
        --query 'tasks[0]' --output json)
    printf '%s' "${task_json}" | \
        EXPECTED_TASK="${expected_task_definition}" \
        EXPECTED_DIGEST="${IMAGE_DIGEST}" python3 -c '
import json, os, sys
task = json.load(sys.stdin)
containers = task.get("containers", [])
if task.get("lastStatus") != "RUNNING" or task.get("healthStatus") != "HEALTHY":
    raise SystemExit("candidate task is not running and healthy")
if task.get("taskDefinitionArn") != os.environ["EXPECTED_TASK"]:
    raise SystemExit("running task definition differs from candidate")
if len(containers) != 1 or containers[0].get("imageDigest") != os.environ["EXPECTED_DIGEST"]:
    raise SystemExit("running image digest differs from built artifact")
'
    curl -fsS \
        --connect-to "dsf-ai.com:443:${ALB_DNS}:443" \
        --connect-timeout 10 --max-time 30 \
        "${CONTROL_ORIGIN}/health" \
        | python3 -c \
            'import json,sys; value=json.load(sys.stdin); assert value.get("status") == "ok"'
    ready_nonce=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    # ``/ready/guala`` takes the transition lock deliberately, so that it can
    # only ever report persisted state -- and that lock is held for a WHOLE
    # lesson.  A 30s cap therefore fails a perfectly healthy body that merely
    # happens to be mid-lesson, which is a false negative, not a safety check.
    # Waiting is the honest behaviour: every assertion below still has to pass.
    ready_body=$(curl -fsS \
        --connect-to "dsf-ai.com:443:${ALB_DNS}:443" \
        --connect-timeout 10 --max-time "${READY_MAX_SECONDS}" \
        -H "X-API-Key: ${DEPLOY_API_KEY}" \
        -H "X-Deploy-Nonce: ${ready_nonce}" \
        "${CONTROL_ORIGIN}/ready/guala")
    printf '%s' "${ready_body}" | \
        EXPECTED_TASK="${expected_task_name}" \
        EXPECTED_DIGEST="${IMAGE_DIGEST}" EXPECTED_SHA="${GIT_SHA}" \
        python3 -c '
import json, os, re, sys
value = json.load(sys.stdin)
if value.get("ready") is not True or value.get("native_state") is not True:
    raise SystemExit("organism did not prove ready native state")
if value.get("task_definition") != os.environ["EXPECTED_TASK"]:
    raise SystemExit("organism reports a different task definition")
if value.get("image_digest") != os.environ["EXPECTED_DIGEST"]:
    raise SystemExit("organism reports a different image digest")
if value.get("git_sha") != os.environ["EXPECTED_SHA"]:
    raise SystemExit("organism reports a different reviewed commit")
if value.get("ready_scope") != "http_native_current_and_admitted_sensory_transitions":
    raise SystemExit("readiness scope is not the reviewed sensory-transitions scope")
native = value.get("native_resident", {})
if native.get("available") is not True:
    raise SystemExit("native resident observation is unavailable")
if native.get("python_callback_count") != 0:
    raise SystemExit("native resident reports Python cognition callbacks")
state_sha = native.get("state_sha256")
if not isinstance(state_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", state_sha):
    raise SystemExit("native resident state identity is absent")
state_bytes = native.get("state_bytes")
if not isinstance(state_bytes, int) or state_bytes <= 0:
    raise SystemExit("native resident state byte count is invalid")
if native.get("persistence_schema") not in {
    "guala.native_organism_binary_store.v1",
}:
    raise SystemExit("native resident persistence schema changed")
# 2026-08-07 correction: the old assertions demanded a body with NO
# neurons and NO cognition -- impossible for any living or newborn body,
# so this gate could never pass and only ran AFTER the cutover.  A living
# continued body (and a fresh genesis alike) has neurons and cognition.
# genuine_neuronal_fractal_available is deliberately NOT asserted: it is
# a last-transition step fact, not body state.
if (
    native.get("complete_neuron_available") is not True
    or native.get("cognition_available") is not True
):
    raise SystemExit("candidate does not present a living cognitive body")
'
    printf '%s' "${task_arns}"
}

drain_live_organism() {
    local service_json running_tasks

    # A persistent body cannot have two writers, even briefly. ECS rolling
    # replacement may start the successor while the retiring task is still
    # completing an atomic unattended interval. Measured in production on
    # 2026-08-17, that overlap let the retiring task advance CURRENT after the
    # successor had begun restoring its predecessor. Stop and verify the sole
    # writer is gone before allowing the successor to start.
    aws ecs update-service \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --service "${ECS_SERVICE}" \
        --desired-count 0 \
        --deployment-configuration "${DEPLOY_CONFIGURATION}" >/dev/null
    aws ecs wait services-stable \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --services "${ECS_SERVICE}"
    service_json=$(aws ecs describe-services \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --services "${ECS_SERVICE}" \
        --query 'services[0]' --output json)
    printf '%s' "${service_json}" | python3 -c '
import json, sys
service = json.load(sys.stdin)
counts = {key: service.get(key) for key in ("desiredCount", "runningCount", "pendingCount")}
if counts != {"desiredCount": 0, "runningCount": 0, "pendingCount": 0}:
    raise SystemExit(f"production writer did not drain exactly: {counts}")
'
    running_tasks=$(aws ecs list-tasks \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --service-name "${ECS_SERVICE}" \
        --desired-status RUNNING \
        --query 'taskArns' --output text)
    if [ -n "${running_tasks}" ] && [ "${running_tasks}" != "None" ]; then
        fail "production retains a running writer after the zero-task drain"
    fi
}

restore_previous_live_organism() {
    # A failed candidate start must not strand production at desired-count
    # zero.  Drain any partial candidate first, then restart the exact task
    # definition that preflight proved was the sole healthy writer.
    aws ecs update-service \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --service "${ECS_SERVICE}" \
        --desired-count 0 \
        --deployment-configuration "${DEPLOY_CONFIGURATION}" >/dev/null
    aws ecs wait services-stable \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --services "${ECS_SERVICE}"
    aws ecs update-service \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --service "${ECS_SERVICE}" \
        --task-definition "${SOURCE_TASK_DEFINITION}" \
        --desired-count 1 \
        --deployment-configuration "${DEPLOY_CONFIGURATION}" \
        --force-new-deployment >/dev/null
    aws ecs wait services-stable \
        --region "${AWS_REGION}" \
        --cluster "${ECS_CLUSTER}" \
        --services "${ECS_SERVICE}"
    curl -fsS \
        --connect-to "dsf-ai.com:443:${ALB_DNS}:443" \
        --connect-timeout 10 --max-time 30 \
        "${CONTROL_ORIGIN}/health" \
        | python3 -c \
            'import json,sys; value=json.load(sys.stdin); assert value.get("status") == "ok"'
}

if [ "${REHEARSE_ONLY}" = "1" ]; then
    echo "[5/7] Rehearsing the digest-pinned candidate without cutover."
    PREVIOUS_RUNNING_TASK="${RUNNING_TASKS}"
    for cutover_number in $(seq 1 "${REPEAT_CUTOVER}"); do
    # Preflight already read and validated the exact persisted live receipt,
    # then proved that ECS topology did not drift during that inspection.
    # Re-reading /ready here duplicated the same large observation and added a
    # second HTTP failure boundary without strengthening continuity.  The
    # read-only probe admits a later CURRENT tick, so the validated predecessor
    # is the exact lower bound it requires while the living source advances.
    REHEARSAL_SOURCE=$(python3 -c '
import json, sys
with open(sys.argv[1], encoding="utf-8") as source:
    predecessor = json.load(source).get("predecessor")
if not isinstance(predecessor, dict):
    raise SystemExit("preflight supplied no validated predecessor")
print(json.dumps(predecessor, separators=(",", ":"), sort_keys=True))
' "${WORK_DIR}/preflight.json")
    REHEARSAL_TICK=$(printf '%s' "${REHEARSAL_SOURCE}" | python3 -c \
        'import json,sys; print(json.load(sys.stdin)["tick"])')
    REHEARSAL_STATE_SHA=$(printf '%s' "${REHEARSAL_SOURCE}" | python3 -c \
        'import json,sys; print(json.load(sys.stdin)["state_sha256"])')
    REHEARSAL_IDENTITY=$(printf '%s' "${REHEARSAL_SOURCE}" | python3 -c \
        'import json,sys; print(json.load(sys.stdin)["identity"])')
    [ "${REHEARSAL_IDENTITY}" = "${GUALA_ORGANISM_IDENTITY}" ] \
        || fail "live organism identity differs from the continuity pin"
    REHEARSAL_PROOF=$(python3 tools/run_guala_candidate_rehearsal_task.py \
        --mode cold-restore \
        --cluster "${ECS_CLUSTER}" \
        --service "${ECS_SERVICE}" \
        --candidate-task-definition "${CANDIDATE_TASK_DEFINITION}" \
        --candidate-git-sha "${GIT_SHA}" \
        --candidate-image-digest "${IMAGE_DIGEST}" \
        --expected-identity "${REHEARSAL_IDENTITY}" \
        --expected-tick "${REHEARSAL_TICK}" \
        --expected-state-sha256 "${REHEARSAL_STATE_SHA}")
    printf '%s\n' "${REHEARSAL_PROOF}"
    printf '%s' "${REHEARSAL_PROOF}" | python3 -c '
import json, re, sys
proof = json.load(sys.stdin)
# Earlier transient witnesses are live-closed and are not replayed.  This gate
# proves exact current continuity plus the fresh full-roster action/consequence
# transaction used by A-009-CADENCE-6B.
if (
    proof.get("a013_thermal_body_rehearsed") is not True
    or proof.get("a013_thermal_body_world_revision_before") != 0
    or proof.get("a013_thermal_body_world_revision_after") != 1
    or proof.get("a013_thermal_body_receptor_count") != 2
    or proof.get("a013_thermal_body_reached_site_counts") != [1, 1]
    or proof.get("a013_thermal_body_episode_port_count") != 111
    or proof.get("a013_thermal_body_episode_sample_count") != 222
    or not isinstance(proof.get("a013_thermal_body_dsf_delivery_count"), int)
    or isinstance(proof["a013_thermal_body_dsf_delivery_count"], bool)
    or proof["a013_thermal_body_dsf_delivery_count"] <= 0
    or proof.get("a013_thermal_body_cold_restore_exact") is not True
    or proof.get("a013_fresh_complete_roster_cold_restore_exact") is not True
    or proof.get("a013_thermal_body_python_callback_count") != 0
    or any(
        not re.fullmatch(r"[0-9a-f]{64}", proof.get(name, ""))
        for name in (
            "a013_thermal_body_transition_receipt_sha256",
            "a013_thermal_body_anatomy_receipt_sha256",
            "a013_thermal_body_world_state_sha256",
            "a013_fresh_complete_roster_state_sha256",
        )
    )
):
    raise SystemExit("A-009 fresh action/consequence rehearsal changed")
'
        GIT_SHA="${GIT_SHA}" IMAGE_DIGEST="${IMAGE_DIGEST}" \
            CANDIDATE_TASK_DEFINITION="${CANDIDATE_TASK_DEFINITION}" \
            REHEARSAL_PROOF="${REHEARSAL_PROOF}" python3 -c '
import json, os
proof = json.loads(os.environ["REHEARSAL_PROOF"])
print(json.dumps({
    "candidate_git_sha": os.environ["GIT_SHA"],
    "candidate_image_digest": os.environ["IMAGE_DIGEST"],
    "candidate_task_definition": os.environ["CANDIDATE_TASK_DEFINITION"],
    "rehearsal_proof": proof,
    "schema": "guala.prepared_candidate.v2",
    "status": "rehearsed_not_deployed",
}, separators=(",", ":"), sort_keys=True))
'
        exit 0
    done
else
    echo "[5/7] Starting and verifying the candidate once."
    PREVIOUS_RUNNING_TASK="${RUNNING_TASKS}"
    for cutover_number in $(seq 1 "${REPEAT_CUTOVER}"); do
        # There can be only one persistent writer.  Stop the predecessor,
        # start the candidate once, and use that same restored process as
        # production.  The former mandatory disposable rehearsal duplicated
        # this complete restore without strengthening single-writer custody.
        drain_live_organism
        if ! aws ecs update-service \
            --region "${AWS_REGION}" \
            --cluster "${ECS_CLUSTER}" \
            --service "${ECS_SERVICE}" \
            --task-definition "${CANDIDATE_TASK_DEFINITION}" \
            --desired-count 1 \
            --deployment-configuration "${DEPLOY_CONFIGURATION}" \
            --force-new-deployment >/dev/null; then
            restore_previous_live_organism \
                || fail "candidate admission and predecessor restoration both failed"
            fail "candidate admission failed; predecessor restored"
        fi
        if ! aws ecs wait services-stable \
            --region "${AWS_REGION}" \
            --cluster "${ECS_CLUSTER}" \
            --services "${ECS_SERVICE}"; then
            restore_previous_live_organism \
                || fail "candidate startup and predecessor restoration both failed"
            fail "candidate startup failed; predecessor restored"
        fi
        if ! CURRENT_RUNNING_TASK=$(verify_live_organism \
            "${CANDIDATE_TASK_DEFINITION}"); then
            restore_previous_live_organism \
                || fail "candidate verification and predecessor restoration both failed"
            fail "candidate verification failed; predecessor restored"
        fi
        if [ "${CURRENT_RUNNING_TASK}" = "${PREVIOUS_RUNNING_TASK}" ]; then
            restore_previous_live_organism \
                || fail "unchanged process and predecessor restoration both failed"
            fail "cutover ${cutover_number} did not replace the running process"
        fi
        PREVIOUS_RUNNING_TASK="${CURRENT_RUNNING_TASK}"
        echo "      cutover ${cutover_number}/${REPEAT_CUTOVER}: verified"
    done
fi

echo "[6/7] Pinning only the live-verified artifact as production-current."
IMAGE_MANIFEST=$(aws ecr batch-get-image \
    --region "${AWS_REGION}" \
    --repository-name "${ECR_REPOSITORY}" \
    --image-ids "imageDigest=${IMAGE_DIGEST}" \
    --query 'images[0].imageManifest' --output text)
[ -n "${IMAGE_MANIFEST}" ] && [ "${IMAGE_MANIFEST}" != "None" ] \
    || fail "verified artifact disappeared from ECR"
aws ecr put-image \
    --region "${AWS_REGION}" \
    --repository-name "${ECR_REPOSITORY}" \
    --image-tag production-current \
    --image-manifest "${IMAGE_MANIFEST}" >/dev/null
PINNED_DIGEST=$(aws ecr describe-images \
    --region "${AWS_REGION}" \
    --repository-name "${ECR_REPOSITORY}" \
    --image-ids imageTag=production-current \
    --query 'imageDetails[0].imageDigest' --output text)
[ "${PINNED_DIGEST}" = "${IMAGE_DIGEST}" ] \
    || fail "production-current does not identify the verified artifact"

FINISHED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "[7/7] Deployment complete."
STARTED_AT="${STARTED_AT}" FINISHED_AT="${FINISHED_AT}" \
GIT_SHA="${GIT_SHA}" \
CANDIDATE_TASK_DEFINITION="${CANDIDATE_TASK_DEFINITION}" \
IMAGE_DIGEST="${IMAGE_DIGEST}" REPEAT_CUTOVER="${REPEAT_CUTOVER}" \
python3 -c '
import json, os
print(json.dumps({
    "schema": "guala.deterministic_deployment.v2",
    "status": "deployed",
    "started_at": os.environ["STARTED_AT"],
    "finished_at": os.environ["FINISHED_AT"],
    "git_sha": os.environ["GIT_SHA"],
    "task_definition": os.environ["CANDIDATE_TASK_DEFINITION"],
    "image_digest": os.environ["IMAGE_DIGEST"],
    "cutovers_verified": int(os.environ["REPEAT_CUTOVER"]),
    "verified_native_state": True,
    "automatic_legacy_rollback": False,
}, sort_keys=True))
'
