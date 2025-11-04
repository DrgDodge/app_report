export interface Client {
    id: number;
    nume: string;
    cui: string;
    adresa: string;
    locatie: string;
    nr_reg_com: string;
    iban: string;
}

export interface Part {
    id: number;
    pn: string;
    descriere: string;
}
