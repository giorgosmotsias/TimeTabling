from ortools.sat.python import cp_model
import json

class SxolikosProgrammatismosProblem():
    '''Δεδομένα του προβλήματος.'''

    def __init__(self, epipeda, tmimata, antikeimena, kyklos_mathimatwn, kathigites,
                 eidikotites, xronikes_periodoi):
        self._epipeda = epipeda
        self._tmimata = tmimata
        self._antikeimena = antikeimena
        self._kyklos_mathimatwn = kyklos_mathimatwn
        assert len(self._kyklos_mathimatwn) == len(self._epipeda) * len(
            self._antikeimena), 'Κάποιος κύκλος μαθημάτων λείπει'
        for (epipedo, eidikotita) in self._kyklos_mathimatwn.keys():
            assert epipedo in self._epipeda, f'{epipedo} δεν υπάρχει στη μεταβλητή EPIPEDA'
            assert eidikotita in self._antikeimena, f'{eidikotita} δεν υπάρχει στη μεταβλητή EIDIKOTITA'

        self._kathigites = kathigites
        self._eidikotites = eidikotites
        assert len(self._eidikotites) == len(
            self._antikeimena), 'Λείπουν κάποιες γραμμές'
        for s, ts in self._eidikotites.items():
            assert s in self._antikeimena, f'{s} δεν υπάρχει στη μεταβλητή ANTIKEIMENA'
            for t in ts:
                assert t in self._kathigites, f'{t} δεν υπάρχει στη μεταβλητή KATHIGITES'

        self._xronikes_periodoi = xronikes_periodoi

    @property
    def epipeda(self):
        return self._epipeda

    @property
    def tmimata(self):
        return self._tmimata

    @property
    def antikeimena(self):
        return self._antikeimena

    @property
    def kyklos_mathimatwn(self):
        return self._kyklos_mathimatwn

    @property
    def kathigites(self):
        return self._kathigites

    def kathigitis_onoma(self, kathigitis_id):
        assert 0 <= kathigitis_id < len(self._kathigites)
        return list(self._kathigites.keys())[kathigitis_id]

    def kathigitis_max_wres(self, kathigitis_id):
        assert 0 <= kathigitis_id < len(self._kathigites)
        return list(self._kathigites.values())[kathigitis_id]

    @property
    def eidikotites(self):
        return self._eidikotites

    def eidikotita_kathigitwn(self, eidikotita):
        assert eidikotita in self._antikeimena, f'{eidikotita} δεν υπάρχει στη μεταβλητή ANTIKEIMENA'
        return self._eidikotites[eidikotita]

    @property
    def xronikes_periodoi(self):
        return self._xronikes_periodoi

    def diarkeia_periodou(self, periodos_id):
        assert 0 <= periodos_id < len(self._xronikes_periodoi)
        return list(self._xronikes_periodoi.values())[periodos_id]


class SxolikosProgrmammatismosSolver():
    '''Παράδειγμα Επίλυσης.'''

    def __init__(self, problem: SxolikosProgrammatismosProblem):
        # Πρόβλημα
        self._problem = problem

        # Υπηρεσίες
        arithmos_epipedwn = len(self._problem.epipeda)
        self._all_epipeda = range(arithmos_epipedwn)
        arithmos_tmimatwn = len(self._problem.tmimata)
        self._all_tmimata = range(arithmos_tmimatwn)
        arithmos_antikeimenwn = len(self._problem.antikeimena)
        self._all_antikeimena = range(arithmos_antikeimenwn)
        arithmos_kathigitwn = len(self._problem.kathigites)
        self._all_kathigites = range(arithmos_kathigitwn)
        arithmos_xronikwn_periodwn = len(self._problem.xronikes_periodoi)
        self._all_xronikes_periodoi = range(arithmos_xronikwn_periodwn)

        # Δημιουργία μοντέλου
        self._model = cp_model.CpModel()

        # Δημιουργία μεταβλητών
        self._assignment = {}
        for epipedo_id, epipedo in enumerate(self._problem.epipeda):
            for tmima_id, tmima in enumerate(self._problem.tmimata):
                for antikeimeno_id, antikeimeno in enumerate(self._problem.antikeimena):
                    for kathigitis_id, kathigitis in enumerate(self._problem.kathigites):
                        for periodos_id, periodos in enumerate(self._problem.xronikes_periodoi):
                            k = (epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id)
                            n = f'{epipedo}-{tmima} S:{antikeimeno} T:{kathigitis} Slot:{periodos}'
                            # Εκτύπωση Ονόματος
                            if kathigitis in self._problem.eidikotita_kathigitwn(antikeimeno):
                                self._assignment[k] = self._model.NewBoolVar(n)
                            else:
                                n = 'NO DISP ' + n
                                self._assignment[k] = self._model.NewIntVar(0, 0, n)

        # !!!ΠΕΡΙΟΡΙΣΜΟΙ!!!
        # Κάθε Τμήμα πρέπει να έχει τον απαραίτητο αριθμό μαθημάτων που προσδιορίζεται από τον Κύκλο Μαθημάτων
        for epipedo_id, epipedo in enumerate(self._problem.epipeda):
            for tmima_id in self._all_tmimata:
                for antikeimeno_id, antikeimeno in enumerate(self._problem.antikeimena):
                    apaitoumeni_diarkeia = self._problem.kyklos_mathimatwn[epipedo, antikeimeno]
                    #print(f'Τάξη:{epipedo} Μάθημα:{antikeimeno} Διάρκεια:{apaitoumeni_diarkeia}h')
                    self._model.Add(
                        sum(self._assignment[epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id] *
                            int(self._problem.diarkeia_periodou(periodos_id) * 10)
                            for kathigitis_id in self._all_kathigites
                            for periodos_id in self._all_xronikes_periodoi) == int(apaitoumeni_diarkeia * 10))

        # Κάθε τμήμα μπορεί να κάνει μόνο ένα μάθημα σε κάθε χρονική περίοδο
        for epipedo_id in self._all_epipeda:
            for tmima_id in self._all_tmimata:
                for periodos_id in self._all_xronikes_periodoi:
                    self._model.Add(
                        sum([
                            self._assignment[epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id]
                            for antikeimeno_id in self._all_antikeimena
                            for kathigitis_id in self._all_kathigites
                        ]) <= 1)

        # Ο Καθηγητής μπορεί να διδάσκει το πολύ σε ένα τμήμα τη φορά
        for kathigitis_id in self._all_kathigites:
            for periodos_id in self._all_xronikes_periodoi:
                self._model.Add(
                    sum([
                        self._assignment[epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id]
                        for epipedo_id in self._all_epipeda
                        for tmima_id in self._all_tmimata
                        for antikeimeno_id in self._all_antikeimena
                    ]) <= 1)

        # Μέγιστες ώρες εργασίας κάθε καθηγητή
        for kathigitis_id in self._all_kathigites:
            self._model.Add(
                sum([
                    self._assignment[epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id] *
                    int(self._problem.diarkeia_periodou(periodos_id) * 10)
                    for epipedo_id in self._all_epipeda
                    for tmima_id in self._all_tmimata
                    for antikeimeno_id in self._all_antikeimena
                    for periodos_id in self._all_xronikes_periodoi
                ]) <= int(self._problem.kathigitis_max_wres(kathigitis_id) * 10))

        # Ο Καθηγητής κάνει όλες τις τάξεις στο ίδιο μάθημα
        mathima_kathigiti = {}
        for epipedo_id, epipedo in enumerate(self._problem.epipeda):
            for tmima_id, tmima in enumerate(self._problem.tmimata):
                for antikeimeno_id, antikeimeno in enumerate(self._problem.antikeimena):
                    for kathigitis_id, kathigitis in enumerate(self._problem.kathigites):
                        n = f'{epipedo}-{tmima} Μάθημα:{antikeimeno} Καθηγητής:{kathigitis}'
                        mathima_kathigiti[epipedo_id, tmima_id, antikeimeno_id, kathigitis_id] = self._model.NewBoolVar(n)
                        temp_array = [
                            self._assignment[epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id]
                            for periodos_id in self._all_xronikes_periodoi
                        ]
                        self._model.AddMaxEquality(
                            mathima_kathigiti[epipedo_id, tmima_id, antikeimeno_id, kathigitis_id], temp_array)
                    self._model.Add(
                        sum([mathima_kathigiti[epipedo_id, tmima_id, antikeimeno_id, kathigitis_id]
                             for kathigitis_id in self._all_kathigites
                             ]) == 1)


    def print_programma_kathigiti(self, kathigitis_id):
        onoma_kathigiti = self._problem.kathigitis_onoma(kathigitis_id)
        print(f'Καθηγητής: {onoma_kathigiti}')
        synolikes_wres_ergasias = 0
        for periodos_id, periodos in enumerate(self._problem.xronikes_periodoi):
            for epipedo_id, epipedo in enumerate(self._problem.epipeda):
                for tmima_id, tmima in enumerate(self._problem.tmimata):
                    for antikeimeno_id, antikeimeno in enumerate(self._problem.antikeimena):
                        key = (epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id)
                        if self._solver.BooleanValue(self._assignment[key]):
                            synolikes_wres_ergasias += self._problem.diarkeia_periodou(periodos_id)
                            print(f'{periodos}: Τμήμα:{epipedo}-{tmima} Μάθημα:{antikeimeno}')
        print(f'Συνολικές ώρες εργασίας: {synolikes_wres_ergasias}h')


    def print_programma_tmimatos(self, epipedo_id, tmima_id):
        epipedo = self._problem.epipeda[epipedo_id]
        tmima = self._problem.tmimata[tmima_id]
        print(f'Τμήμα: {epipedo}-{tmima}')
        synolikes_wres_ergasias = {}
        for ant in self._problem.antikeimena:
            synolikes_wres_ergasias[ant] = 0
        for periodos_id, periodos in enumerate(self._problem.xronikes_periodoi):
            for kathigitis_id, kathigitis in enumerate(self._problem.kathigites):
                for antikeimeno_id, antikeimeno in enumerate(self._problem.antikeimena):
                    key = (epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id)
                    if self._solver.BooleanValue(self._assignment[key]):
                        synolikes_wres_ergasias[antikeimeno] += self._problem.diarkeia_periodou(periodos_id)
                        print(f'{periodos}: Μάθημα:{antikeimeno} Καθηγητής:{kathigitis}')
        for (antikeimeno, wres) in synolikes_wres_ergasias.items():
            print(f'Συνολικές ώρες εργασίας για {antikeimeno}: {wres}h')


    def print_programma_sxoleiou(self):
        print('Σχολείο:')
        for periodos_id, periodos in enumerate(self._problem.xronikes_periodoi):
            tmp = f'{periodos}:'
            for epipedo_id, epipedo in enumerate(self._problem.epipeda):
                for tmima_id, tmima in enumerate(self._problem.tmimata):
                    for antikeimeno_id, antikeimeno in enumerate(self._problem.antikeimena):
                        for kathigitis_id, kathigitis in enumerate(self._problem.kathigites):
                            key = (epipedo_id, tmima_id, antikeimeno_id, kathigitis_id, periodos_id)
                            if self._solver.BooleanValue(self._assignment[key]):
                                tmp += f' {epipedo}-{tmima}:({antikeimeno},{kathigitis})'
            print(tmp)


    def solve(self):
        print('Επίλυση...')
        # Create Solver
        self._solver = cp_model.CpSolver()

        solution_printer = SxolikosProgrammatismosSatSolutionPrinter()
        status = self._solver.Solve(self._model, solution_printer)
        print('Κατάσταση: ', self._solver.StatusName(status))

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print('\n# Καθηγητές')
            for kathigitis_id in self._all_kathigites:
                self.print_programma_kathigiti(kathigitis_id)

            print('\n# Τμήματα ')
            for epipedo_id in self._all_epipeda:
                for tmima_id in self._all_tmimata:
                    self.print_programma_tmimatos(epipedo_id, tmima_id)

            print('\n# Σχολείο ')
            self.print_programma_sxoleiou()

        print('\nΔιακλάδωση: ', self._solver.NumBranches())
        print('Συγκρούσεις: ', self._solver.NumConflicts())
        print('Χρόνος εκτέλεσης: ', self._solver.WallTime())


class SxolikosProgrammatismosSatSolutionPrinter(cp_model.CpSolverSolutionCallback):

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0

    def OnSolutionCallback(self):
        print(
            f'Λύση #{self.__solution_count}, αντικείμενο: {self.ObjectiveValue()}'
        )
        self.__solution_count += 1


def main():


    with open("DATA.json") as DATA:
        data = json.load(DATA)

        EPIPEDA = data["EPIPEDA"]
        print("              ΕΠΙΠΕΔΑ              ")
        print("___________________________________")
        for i in range(len(EPIPEDA)):
            print(EPIPEDA[i])

        TMHMATA = data["TMHMATA"]
        print("              TMHMATA              ")
        print("___________________________________")
        for i in range(len(TMHMATA)):
            print(TMHMATA[i])

        dict0 = data["ANTIKEIMENA"]
        ANTIKEIMENA = []
        for i in range(len(dict0)):
            temp = dict0[i]
            ANTIKEIMENA.append(temp["mathima"])
        print("            ANTIKEIMENA            ")
        print("-----------------------------------")
        for i in range(len(ANTIKEIMENA)):
            print(i + 1, ANTIKEIMENA[i])

        dict1 = data["KYKLOS_MATHIMATWN"]
        KYKLOS_MATHIMATWN = {}
        for i in range(len(dict1)):
            temp = dict1[i]
            KYKLOS_MATHIMATWN[temp["epipedo"], temp["antikeimeno"]] = temp["wres"]
        print("___________________________________________________________")
        print("                    ΚΥΚΛΟΣ ΜΑΘΗΜΑΤΩΝ                       ")
        print("___________________________________________________________")
        print("{:<50} {:<40}".format("ΤΑΞΗ, ΑΝΤΙΚΕΙΜΕΝΟ", "ΩΡΕΣ"))
        print("___________________________________________________________")
        for key, value in KYKLOS_MATHIMATWN.items():
            temp = str(key)
            print("{:<50} {:<40}".format(temp, value))

        dict2 = data["KATHIGITES"]
        KATHIGITES = {}
        temp_dict = {}
        EIDIKOTITES = temp_dict.fromkeys(ANTIKEIMENA)

        for i in range(len(dict2)):
            temp = dict2[i]
            KATHIGITES[temp["onoma"]] = temp["wres"]

            for j in range(len(dict0)):
                ant = dict0[j]
                if type(temp["eidikotita"]) == str:
                    if temp["eidikotita"] == ant["eidikotita"]:
                        mathima = ant["mathima"]
                        if type(EIDIKOTITES[mathima]) == list:
                            EIDIKOTITES[mathima].append(temp["onoma"])
                        else:
                            EIDIKOTITES[mathima] = [temp["onoma"]]
                    else:
                        pass
                elif type(temp["eidikotita"]) == list:
                    for k in range(len(temp["eidikotita"])):
                        if temp["eidikotita"][k] == ant["eidikotita"]:
                            mathima = ant["mathima"]
                            if type(EIDIKOTITES[mathima]) == list:
                                EIDIKOTITES[mathima].append(temp["onoma"])
                            else:
                                EIDIKOTITES[mathima] = [temp["onoma"]]
                        else:
                            pass
                else:
                    pass

        print("___________________________________________________________")
        print("{:<40} {:<20}".format('ΚΑΘΗΓΗΤΕΣ', 'ΜΕΓΙΣΤΕΣ ΩΡΕΣ'))
        print("___________________________________________________________")
        for key, value in KATHIGITES.items():
            print("{:<40} {:<20}".format(key, value))

        print("___________________________________________________________")
        print("{:<40} {:<20}".format('ANTIKEIMENO', 'ΔΙΑΘΕΣΙΜΟΙ ΚΑΘΗΓΗΤΕΣ'))
        print("___________________________________________________________")
        for key, value in EIDIKOTITES.items():
            temp = str(value)
            print("{:<40} {:<20}".format(key, temp))

        dict3 = data["Xronikes_Periodoi"]
        XRONIKES_PERIODOI = {}
        for i in range(len(dict3)):
            temp = dict3[i]
            XRONIKES_PERIODOI[temp["Mera-Wres"]] = temp["Diarkeia"]

        print("___________________________________________________________")
        print("{:<40} {:<20}".format('ΜΕΡΑ:    ΩΡΕΣ', 'ΔΙΑΡΚΕΙΑ'))
        print("___________________________________________________________")
        for key, value in XRONIKES_PERIODOI.items():
            print("{:<40} {:<20}".format(key, value))

    problem = SxolikosProgrammatismosProblem(EPIPEDA, TMHMATA, ANTIKEIMENA, KYKLOS_MATHIMATWN, KATHIGITES, EIDIKOTITES,
                                             XRONIKES_PERIODOI)
    solver = SxolikosProgrmammatismosSolver(problem)
    solver.solve()


main()
