from typing import List
from zipfile import ZipFile
from json import loads, dumps
from requests import get
from gensim.models import KeyedVectors
from procemon.paths import MOVES_DIRECTORY, WORD_VEC_DIRECTORY, TYPES_DIRECTORY


class WV:
    """
    Use a word vector model to assign verbs and adjectives to monster types.
    These are stored in the .json monster type files.
    """

    def __init__(self, quiet: bool = False):
        """
        :param quiet: If True, suppress console output.
        """

        """:field
        If True, suppress console output.
        """
        self.quiet = quiet
        """:field
        A list of all possible verbs.
        """
        self.verbs: List[str] = MOVES_DIRECTORY.joinpath("verbs.txt").read_text(encoding="utf-8").split("\n")
        # Remove auxiliary verbs.
        aux_verbs: List[str] = MOVES_DIRECTORY.joinpath("auxiliary_verbs.txt").read_text(encoding="utf-8").split("\n")
        self.verbs = [v for v in self.verbs if v not in aux_verbs]
        """:field
        A list of all possible adjectives.
        """
        self.adjectives: List[str] = MOVES_DIRECTORY.joinpath("adjectives.txt").read_text(encoding="utf-8").split("\n")
        """:field
        The word vectors model.
        """
        self.wv: KeyedVectors = self.get_word_vector_model()

    def get_word_vector_model(self) -> KeyedVectors:
        """
        Get the loaded WordVector model. Download the file if it doesn't already exist.

        :return: The word vector KeyedVectors model.
        """

        if not WORD_VEC_DIRECTORY.exists():
            WORD_VEC_DIRECTORY.mkdir(parents=True)
        word_vec_path = WORD_VEC_DIRECTORY.joinpath("glove.txt")
        # Get the word vector file.
        if not word_vec_path.exists():
            if not self.quiet:
                print("No word vector model file found. Downloading one now...")
            resp = get("https://github.com/subalterngames/procemon/releases/download/wv/glove.zip")
            assert resp.status_code == 200, f"Tried to download word vector model but got error code {resp.status_code}"
            zip_path = WORD_VEC_DIRECTORY.joinpath("glove.zip")
            zip_path.write_bytes(resp.content)
            with ZipFile(str(zip_path.resolve()), 'r') as zip_ref:
                zip_ref.extractall(str(WORD_VEC_DIRECTORY.resolve()))
            if not self.quiet:
                print("Unzipped.")
            zip_path.unlink()
            if not self.quiet:
                print("Deleted the zip file.")
        if not self.quiet:
            print("Loading word vector model (be patient!)...")
        return KeyedVectors.load_word2vec_format(str(word_vec_path.resolve()), binary=False)

    def get_attack_verbs(self, distance: float = 0.5, write: bool = False) -> List[str]:
        """
        :param distance: The verb must be this close to an "attack verb".
        :param write: If True, write the list to disk.

        :return: A list of all verbs that are nearby an "attack" verb.
        """

        attack_verbs: List[str] = list()
        for v in self.verbs:
            if len(v) <= 3:
                continue
            done = False
            for av in ["attack", "assault", "battle", "clash", "kill", "fight", "punch", "kick", "slash", "strike",
                       "defend"]:
                if done:
                    break
                # If the verb is nearby an "attack verb", add it to the list.
                try:
                    d = self.wv.distance(v, av)
                    if d < distance:
                        attack_verbs.append(v)
                        done = True
                # This word isn't isn't in the word vector model. Ignore it.
                except KeyError:
                    done = True
        # Remove duplicates.
        attack_verbs = list(sorted(set(attack_verbs)))
        # Write the list to disk.
        if write:
            MOVES_DIRECTORY.joinpath("attack_verbs.txt").write_text("\n".join(attack_verbs), encoding="utf-8")
            if not self.quiet:
                print("Got attack verbs and wrote them to disk.")
        return attack_verbs

    def get_type_verbs(self, monster_type: str) -> List[str]:
        """
        :param monster_type: The monster type name string.

        :return: A list of verbs nearby the monster type word.
        """

        # "Action verbs" aren't attack verbs because they're further away.
        # We'll use this to sort out bad verbs for the monster types.
        action_verb_distance = 0.6
        type_verbs: List[str] = list()

        # Get enough verbs for this type.
        # If we don't get enough verbs, increase the maximum action verb distance and try again.
        while action_verb_distance < 1 and len(type_verbs) < 8:
            action_verbs: List[str] = self.get_attack_verbs(distance=action_verb_distance)
            for v in self.verbs:
                if len(v) <= 3 or v not in action_verbs or v in type_verbs:
                    continue
                # If the verb is nearby the monster type, add it to the list.
                try:
                    d = self.wv.distance(v, monster_type)
                    if d < 0.6:
                        type_verbs.append(v)
                # This word isn't isn't in the word vector model. Ignore it.
                except KeyError:
                    continue
            action_verb_distance += 0.1
        return list(sorted(set(type_verbs)))

    def get_type_adjectives(self, monster_type: str) -> List[str]:
        """
        :param monster_type: The monster type name string.

        :return: A list of adjectives nearby the monster type word.
        """

        type_adjectives: List[str] = list()
        for a in self.adjectives:
            # If the adjecties is nearby the monster type, add it to the list.
            try:
                d = self.wv.distance(a, monster_type)
                if d < 0.6:
                    type_adjectives.append(a)
            # This word isn't isn't in the word vector model. Ignore it.
            except KeyError:
                continue
        return list(sorted(set(type_adjectives)))


if __name__ == "__main__":
    wv = WV()
    # Get attack verbs.
    MOVES_DIRECTORY.joinpath("attack_verbs.txt").write_text("\n".join(wv.get_attack_verbs()), encoding="utf-8")
    all_types: List[str] = list()
    # Get verbs and adjectives for each monster type.
    for f in TYPES_DIRECTORY.iterdir():
        monster_data = loads(f.read_text(encoding="utf-8"))
        mt: str = monster_data["monster_type"]
        print(mt)
        mv = wv.get_type_verbs(mt)
        print(f"\tVerbs: {mv}")
        ma = wv.get_type_adjectives(mt)
        print(f"\tAdjectives: {ma}")
        monster_data["verbs"] = mv
        monster_data["adjectives"] = ma
        f.write_text(dumps(monster_data, sort_keys=True, indent=2), encoding="utf-8")
